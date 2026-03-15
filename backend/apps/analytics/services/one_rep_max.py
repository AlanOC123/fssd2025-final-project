from decimal import Decimal

from apps.analytics.constants import epley_one_rep_max
from apps.analytics.services.load import calculate_session_load
from apps.workouts.models import WorkoutCompletionRecord


def get_program_1rm_for_exercise(program, exercise):

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

    all_sets = [
        sr for er in set_records for sr in er.set_records.all() if not sr.is_skipped
    ]

    return calculate_session_load(all_sets)
