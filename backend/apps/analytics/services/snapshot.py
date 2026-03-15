from decimal import ROUND_HALF_UP, Decimal

from apps.analytics.constants import epley_one_rep_max, weight_at_reps
from apps.analytics.models import ExerciseSessionSnapshot
from apps.analytics.services.load import calculate_session_load
from apps.workouts.models import WorkoutCompletionRecord, WorkoutSetCompletionRecord


def _rolling_1rm(program, exercise, up_to_session):

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
    experience_level = program.experience_level
    training_goal = program.training_goal

    cap = experience_level.progression_cap_percent
    rep_min = training_goal.rep_range_min
    rep_max = training_goal.rep_range_max

    # Current session load — what the client just did
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

    # Skip snapshot if this exercise had no valid sets this session
    if current_load == Decimal("0"):
        return None

    # Rolling 1RM — includes current session, never decreases
    one_rm = _rolling_1rm(program, exercise, up_to_session=session)
    if one_rm is None:
        return None

    one_rm = one_rm.quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)

    # Previous session load drives the next target
    prev_load = _previous_session_load(program, exercise, before_session=session)
    target_load = (
        (prev_load * (1 + cap)).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)
        if prev_load > Decimal("0") and cap is not None
        else None
    )

    # Weight band from 1RM + NSCA + training goal
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
