from decimal import ROUND_HALF_UP, Decimal

from apps.analytics.constants import epley_one_rep_max, weight_at_reps
from apps.analytics.services.load import calculate_session_load
from apps.workouts.models import WorkoutCompletionRecord


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
    from apps.workouts.models import WorkoutSetCompletionRecord

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
