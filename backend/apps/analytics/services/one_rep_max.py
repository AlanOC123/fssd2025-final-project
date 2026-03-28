from decimal import Decimal

from apps.analytics.constants import epley_one_rep_max
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
