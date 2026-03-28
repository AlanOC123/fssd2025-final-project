from decimal import ROUND_HALF_UP, Decimal

from apps.analytics.constants import epley_one_rep_max, weight_at_reps
from apps.analytics.models import ExerciseSessionSnapshot
from apps.analytics.services.load import calculate_session_load
from apps.workouts.models import WorkoutCompletionRecord, WorkoutSetCompletionRecord


def get_program_1rm_for_exercise(program, exercise):
    """Calculates the maximum estimated 1RM for an exercise within a specific program.

    Iterates through all completed non-skipped sets for the given exercise
    across all phases of the program to find the highest calculated Epley 1RM.

    Args:
        program: The Program instance to filter by.
        exercise: The Exercise instance to calculate the 1RM for.

    Returns:
        Optional[float]: The highest calculated 1RM across all records, or None
            if no records exist for the given exercise and program.
    """
    set_records = WorkoutSetCompletionRecord.objects.filter(
        workout_set__workout_exercise__exercise=exercise,
        workout_set__workout_exercise__workout__program_phase__program=program,
        is_skipped=False,
    ).select_related("workout_set")

    if not set_records.exists():
        return None

    return max(
        epley_one_rep_max(s.weight_completed, s.reps_completed) for s in set_records
    )


def get_last_session_load_for_exercise(program, exercise):
    """Retrieves the total volume load from the most recent session of an exercise.

    Args:
        program: The Program instance to filter by.
        exercise: The Exercise instance to retrieve the last load for.

    Returns:
        Decimal: The total calculated load (weight * reps) for the most recent
            session. Returns 0.00 if no previous sessions are found.
    """
    last_session = (
        WorkoutCompletionRecord.objects.filter(
            workout__program_phase__program=program,
            workout__exercises__exercise=exercise,
            completed_at__isnull=False,
            is_skipped=False,
        )
        .order_by("-completed_at")
        .first()
    )

    if not last_session:
        return Decimal("0.00")

    set_records = last_session.exercise_records.filter(
        workout_exercise__exercise=exercise, is_skipped=False
    ).prefetch_related("set_records")

    # Flatten set records from exercise records while ensuring skipped sets are excluded
    all_sets = [
        sr for er in set_records for sr in er.set_records.all() if not sr.is_skipped
    ]

    return calculate_session_load(all_sets)


def get_next_session_recommendation(program, exercise):
    """Generates training weight and load recommendations for the next session.

    Calculates recommended weight ranges (floor and ceiling) and target volume load
    based on the user's experience level, training goals, and historical performance
    within a specific program.

    Args:
        program: The Program instance containing training parameters like
            experience level and training goal.
        exercise: The Exercise instance to generate recommendations for.

    Returns:
        Optional[dict]: A dictionary containing recommendation details including
            calculated 1RM, target load, weight ranges, and constraints.
            Returns None if membership or required progression metrics are missing.
    """
    membership = program.trainer_client_membership

    if not membership:
        return None

    experience_level = program.experience_level
    training_goal = program.training_goal

    cap = experience_level.progression_cap_percent
    rep_min = training_goal.rep_range_min
    rep_max = training_goal.rep_range_max

    if cap is None or rep_min is None or rep_max is None:
        return None

    one_rm = get_program_1rm_for_exercise(program, exercise)
    if one_rm is None:
        return None

    last_load = get_last_session_load_for_exercise(program, exercise)
    target_load = last_load * (1 + cap) if last_load > 0 else None

    # Calculate weight boundaries based on required rep ranges and estimated 1RM
    weight_floor = weight_at_reps(one_rm, rep_max).quantize(
        Decimal("0.01"), rounding=ROUND_HALF_UP
    )

    weight_ceiling = weight_at_reps(one_rm, rep_min).quantize(
        Decimal("0.01"), rounding=ROUND_HALF_UP
    )

    return {
        "exercise": exercise,
        "one_rep_max": one_rm.quantize(Decimal("0.01"), rounding=ROUND_HALF_UP),
        "last_session_load": last_load,
        "target_load": target_load,
        "rep_range_min": rep_min,
        "rep_range_max": rep_max,
        "weight_floor": weight_floor,
        "weight_ceiling": weight_ceiling,
        "progression_cap_percent": cap,
    }


def _rolling_1rm(program, exercise, up_to_session):
    """Calculates the 1RM based on all data up to and including a specific session.

    Args:
        program: The Program instance to filter by.
        exercise: The Exercise instance to calculate the 1RM for.
        up_to_session: The WorkoutCompletionRecord representing the upper time bound.

    Returns:
        Optional[Decimal]: The highest calculated 1RM found up to that point in time,
            or None if no records exist.
    """
    records = WorkoutSetCompletionRecord.objects.filter(
        workout_set__workout_exercise__exercise=exercise,
        workout_set__workout_exercise__workout__program_phase__program=program,
        exercise_completion_record__workout_completion_record__completed_at__lte=(
            up_to_session.completed_at
        ),
        is_skipped=False,
    ).select_related("workout_set")

    if not records.exists():
        return None

    return max(epley_one_rep_max(r.weight_completed, r.reps_completed) for r in records)


def _previous_session_load(program, exercise, before_session):
    """Retrieves volume load for the exercise from the session prior to the one provided.

    Args:
        program: The Program instance to filter by.
        exercise: The Exercise instance to retrieve the load for.
        before_session: The WorkoutCompletionRecord session to look before.

    Returns:
        Decimal: The total volume load from the previous session, or 0 if none found.
    """
    prev_session = (
        WorkoutCompletionRecord.objects.filter(
            workout__program_phase__program=program,
            workout__exercises__exercise=exercise,
            completed_at__lt=before_session.completed_at,
            is_skipped=False,
        )
        .order_by("-completed_at")
        .first()
    )

    if not prev_session:
        return Decimal("0")

    set_records = [
        sr
        for er in prev_session.exercise_records.filter(
            workout_exercise__exercise=exercise,
            is_skipped=False,
        ).prefetch_related("set_records")
        for sr in er.set_records.all()
        if not sr.is_skipped
    ]
    return calculate_session_load(set_records)


def compute_and_save_snapshot(program, exercise, session):
    """Persists a snapshot of exercise performance and targets for a specific session.

    Captures the current session's volume load, rolling 1RM, and calculated targets
    for future sessions based on progression caps and training goals.

    Args:
        program: The Program instance associated with the training.
        exercise: The Exercise instance being tracked.
        session: The WorkoutCompletionRecord representing the current session.

    Returns:
        Optional[ExerciseSessionSnapshot]: The saved snapshot instance, or None if
            no load was recorded or 1RM could not be calculated.
    """
    experience_level = program.experience_level
    training_goal = program.training_goal

    cap = experience_level.progression_cap_percent
    rep_min = training_goal.rep_range_min
    rep_max = training_goal.rep_range_max

    # Extract all non-skipped set records for the current session to calculate load
    set_records = [
        sr
        for er in session.exercise_records.filter(
            workout_exercise__exercise=exercise,
            is_skipped=False,
        ).prefetch_related("set_records")
        for sr in er.set_records.all()
        if not sr.is_skipped
    ]
    current_load = calculate_session_load(set_records)

    if current_load == Decimal("0"):
        return None

    one_rm = _rolling_1rm(program, exercise, up_to_session=session)
    if one_rm is None:
        return None

    one_rm = one_rm.quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)

    prev_load = _previous_session_load(program, exercise, before_session=session)
    target_load = (
        (prev_load * (1 + cap)).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)
        if prev_load > Decimal("0") and cap is not None
        else None
    )

    weight_floor = None
    weight_ceiling = None
    if rep_min is not None and rep_max is not None:
        weight_floor = weight_at_reps(one_rm, rep_max).quantize(
            Decimal("0.01"), rounding=ROUND_HALF_UP
        )
        weight_ceiling = weight_at_reps(one_rm, rep_min).quantize(
            Decimal("0.01"), rounding=ROUND_HALF_UP
        )

    snapshot, _ = ExerciseSessionSnapshot.objects.update_or_create(
        program=program,
        exercise=exercise,
        session=session,
        defaults={
            "one_rep_max": one_rm,
            "session_load": current_load.quantize(
                Decimal("0.01"), rounding=ROUND_HALF_UP
            ),
            "target_load": target_load,
            "weight_floor": weight_floor,
            "weight_ceiling": weight_ceiling,
        },
    )
    return snapshot
