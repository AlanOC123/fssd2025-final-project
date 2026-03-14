# apps/workouts/tests/test_models_completion.py

from decimal import Decimal

import pytest
from django.core.exceptions import ValidationError
from django.utils import timezone

from factories import (
    WorkoutCompletionRecordFactory,
    WorkoutExerciseCompletionRecordFactory,
    WorkoutSetCompletionRecordFactory,
)

pytestmark = pytest.mark.django_db


# ─── WorkoutCompletionRecord ──────────────────────────────────────────────────


class TestWorkoutCompletionRecord:

    def test_skipped_record_can_have_completed_at(self, workout, client_user):
        now = timezone.now()
        record = WorkoutCompletionRecordFactory(
            workout=workout,
            client=client_user,
            is_skipped=True,
            started_at=now,
            completed_at=now,
        )
        assert record.pk is not None
        assert record.is_skipped is True
        assert record.completed_at is not None

    def test_completed_at_cannot_be_before_started_at(self, workout, client_user):
        now = timezone.now()
        record = WorkoutCompletionRecordFactory.build(
            workout=workout,
            client=client_user,
            started_at=now,
            completed_at=now - timezone.timedelta(seconds=60),
        )
        with pytest.raises(
            ValidationError, match="completed_at cannot be before started_at"
        ):
            record.full_clean()

    def test_duration_s_returns_elapsed_seconds(self, workout, client_user):
        now = timezone.now()
        record = WorkoutCompletionRecordFactory(
            workout=workout,
            client=client_user,
            started_at=now - timezone.timedelta(seconds=3600),
            completed_at=now,
        )
        assert record.duration_s == 3600

    def test_duration_s_returns_none_when_not_completed(self, workout, client_user):
        record = WorkoutCompletionRecordFactory(
            workout=workout,
            client=client_user,
            completed_at=None,
        )
        assert record.duration_s is None

    def test_workout_can_only_have_one_completion_record(self, workout, client_user):
        WorkoutCompletionRecordFactory(workout=workout, client=client_user)
        duplicate = WorkoutCompletionRecordFactory.build(
            workout=workout,
            client=client_user,
        )
        with pytest.raises(ValidationError):
            duplicate.full_clean()

    def test_valid_skipped_record_has_no_completed_at(self, workout, client_user):
        record = WorkoutCompletionRecordFactory(
            workout=workout,
            client=client_user,
            is_skipped=True,
            completed_at=None,
        )
        assert record.is_skipped is True
        assert record.completed_at is None


# ─── WorkoutExerciseCompletionRecord ─────────────────────────────────────────


class TestWorkoutExerciseCompletionRecord:

    def test_skipped_exercise_can_have_completed_at(
        self, workout_exercise, workout, client_user
    ):
        now = timezone.now()
        session = WorkoutCompletionRecordFactory(
            workout=workout, client=client_user, started_at=now
        )
        record = WorkoutExerciseCompletionRecordFactory(
            workout_completion_record=session,
            workout_exercise=workout_exercise,
            is_skipped=True,
            started_at=now,
            completed_at=now,
        )
        assert record.pk is not None
        assert record.is_skipped is True
        assert record.completed_at is not None

    def test_completed_at_cannot_be_before_started_at(
        self, workout_exercise, workout, client_user
    ):
        now = timezone.now()
        session = WorkoutCompletionRecordFactory(workout=workout, client=client_user)
        record = WorkoutExerciseCompletionRecordFactory.build(
            workout_completion_record=session,
            workout_exercise=workout_exercise,
            started_at=now,
            completed_at=now - timezone.timedelta(seconds=30),
        )
        with pytest.raises(
            ValidationError, match="completed_at cannot be before started_at"
        ):
            record.full_clean()

    def test_exercise_can_only_have_one_completion_record(
        self, workout_exercise, workout, client_user
    ):
        session = WorkoutCompletionRecordFactory(workout=workout, client=client_user)
        WorkoutExerciseCompletionRecordFactory(
            workout_completion_record=session,
            workout_exercise=workout_exercise,
        )
        duplicate = WorkoutExerciseCompletionRecordFactory.build(
            workout_completion_record=session,
            workout_exercise=workout_exercise,
        )
        with pytest.raises(ValidationError):
            duplicate.full_clean()

    def test_valid_active_exercise_record_saves(
        self, workout_exercise, workout, client_user
    ):
        session = WorkoutCompletionRecordFactory(workout=workout, client=client_user)
        record = WorkoutExerciseCompletionRecordFactory(
            workout_completion_record=session,
            workout_exercise=workout_exercise,
        )
        assert record.pk is not None
        assert record.is_skipped is False


# ─── WorkoutSetCompletionRecord ───────────────────────────────────────────────


class TestWorkoutSetCompletionRecord:

    def test_completed_set_requires_reps_greater_than_zero(
        self, workout_set, workout_exercise, workout, client_user
    ):
        session = WorkoutCompletionRecordFactory(workout=workout, client=client_user)
        exercise_record = WorkoutExerciseCompletionRecordFactory(
            workout_completion_record=session,
            workout_exercise=workout_exercise,
        )
        record = WorkoutSetCompletionRecordFactory.build(
            exercise_completion_record=exercise_record,
            workout_set=workout_set,
            is_skipped=False,
            reps_completed=0,
        )
        with pytest.raises(
            ValidationError, match="reps_completed must be greater than 0"
        ):
            record.full_clean()

    def test_completed_set_requires_completed_at(
        self, workout_set, workout_exercise, workout, client_user
    ):
        session = WorkoutCompletionRecordFactory(workout=workout, client=client_user)
        exercise_record = WorkoutExerciseCompletionRecordFactory(
            workout_completion_record=session,
            workout_exercise=workout_exercise,
        )
        record = WorkoutSetCompletionRecordFactory.build(
            exercise_completion_record=exercise_record,
            workout_set=workout_set,
            is_skipped=False,
            completed_at=None,
        )
        with pytest.raises(
            ValidationError, match="completed set must have a completed_at"
        ):
            record.full_clean()

    def test_weight_completed_cannot_be_negative(
        self, workout_set, workout_exercise, workout, client_user
    ):
        session = WorkoutCompletionRecordFactory(workout=workout, client=client_user)
        exercise_record = WorkoutExerciseCompletionRecordFactory(
            workout_completion_record=session,
            workout_exercise=workout_exercise,
        )
        record = WorkoutSetCompletionRecordFactory.build(
            exercise_completion_record=exercise_record,
            workout_set=workout_set,
            is_skipped=False,
            weight_completed=Decimal("-1.00"),
        )
        with pytest.raises(
            ValidationError, match="weight_completed cannot be negative"
        ):
            record.full_clean()

    def test_difficulty_rating_must_be_between_1_and_10(
        self, workout_set, workout_exercise, workout, client_user
    ):
        session = WorkoutCompletionRecordFactory(workout=workout, client=client_user)
        exercise_record = WorkoutExerciseCompletionRecordFactory(
            workout_completion_record=session,
            workout_exercise=workout_exercise,
        )
        for bad_value in [0, 11]:
            record = WorkoutSetCompletionRecordFactory.build(
                exercise_completion_record=exercise_record,
                workout_set=workout_set,
                difficulty_rating=bad_value,
            )
            with pytest.raises(
                ValidationError, match="difficulty_rating must be between 1 and 10"
            ):
                record.full_clean()

    def test_skipped_set_bypasses_reps_and_weight_validation(
        self, workout_set, workout_exercise, workout, client_user
    ):
        session = WorkoutCompletionRecordFactory(workout=workout, client=client_user)
        exercise_record = WorkoutExerciseCompletionRecordFactory(
            workout_completion_record=session,
            workout_exercise=workout_exercise,
        )
        record = WorkoutSetCompletionRecordFactory(
            exercise_completion_record=exercise_record,
            workout_set=workout_set,
            is_skipped=True,
            reps_completed=0,
            weight_completed=Decimal("0.00"),
            completed_at=None,
        )
        assert record.pk is not None

    def test_reps_diff_is_correct(
        self, workout_set, workout_exercise, workout, client_user
    ):
        session = WorkoutCompletionRecordFactory(workout=workout, client=client_user)
        exercise_record = WorkoutExerciseCompletionRecordFactory(
            workout_completion_record=session,
            workout_exercise=workout_exercise,
        )
        # workout_set has reps_prescribed=5
        record = WorkoutSetCompletionRecordFactory(
            exercise_completion_record=exercise_record,
            workout_set=workout_set,
            reps_completed=7,
        )
        assert record.reps_diff == 2

    def test_weight_diff_is_correct(
        self, workout_set, workout_exercise, workout, client_user
    ):
        session = WorkoutCompletionRecordFactory(workout=workout, client=client_user)
        exercise_record = WorkoutExerciseCompletionRecordFactory(
            workout_completion_record=session,
            workout_exercise=workout_exercise,
        )
        # workout_set has weight_prescribed=100.00
        record = WorkoutSetCompletionRecordFactory(
            exercise_completion_record=exercise_record,
            workout_set=workout_set,
            weight_completed=Decimal("102.50"),
        )
        assert record.weight_diff == Decimal("2.50")

    def test_reps_diff_returns_none_when_skipped(
        self, workout_set, workout_exercise, workout, client_user
    ):
        session = WorkoutCompletionRecordFactory(workout=workout, client=client_user)
        exercise_record = WorkoutExerciseCompletionRecordFactory(
            workout_completion_record=session,
            workout_exercise=workout_exercise,
        )
        record = WorkoutSetCompletionRecordFactory(
            exercise_completion_record=exercise_record,
            workout_set=workout_set,
            is_skipped=True,
            reps_completed=0,
            weight_completed=Decimal("0.00"),
            completed_at=None,
        )
        assert record.reps_diff is None
        assert record.weight_diff is None

    def test_set_can_only_have_one_completion_record(
        self, workout_set, workout_exercise, workout, client_user
    ):
        session = WorkoutCompletionRecordFactory(workout=workout, client=client_user)
        exercise_record = WorkoutExerciseCompletionRecordFactory(
            workout_completion_record=session,
            workout_exercise=workout_exercise,
        )
        WorkoutSetCompletionRecordFactory(
            exercise_completion_record=exercise_record,
            workout_set=workout_set,
        )
        duplicate = WorkoutSetCompletionRecordFactory.build(
            exercise_completion_record=exercise_record,
            workout_set=workout_set,
        )
        with pytest.raises(ValidationError):
            duplicate.full_clean()
