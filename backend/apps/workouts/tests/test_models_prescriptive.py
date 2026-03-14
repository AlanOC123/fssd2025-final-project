# apps/workouts/tests/test_models_prescriptive.py

from decimal import Decimal

import pytest
from django.core.exceptions import ValidationError

from factories import (
    WorkoutExerciseFactory,
    WorkoutFactory,
    WorkoutSetFactory,
)

pytestmark = pytest.mark.django_db


# ─── WorkoutExercise ──────────────────────────────────────────────────────────


class TestWorkoutExercise:

    def test_sets_prescribed_zero_is_invalid(self, workout, exercise):
        we = WorkoutExerciseFactory.build(
            workout=workout,
            exercise=exercise,
            sets_prescribed=0,
        )
        with pytest.raises(
            ValidationError, match="sets_prescribed must be greater than 0"
        ):
            we.full_clean()

    def test_sets_prescribed_positive_is_valid(self, workout, exercise):
        we = WorkoutExerciseFactory(
            workout=workout,
            exercise=exercise,
            sets_prescribed=4,
        )
        assert we.sets_prescribed == 4

    def test_order_must_be_unique_within_workout(self, workout, exercise):
        WorkoutExerciseFactory(workout=workout, exercise=exercise, order=1)
        duplicate = WorkoutExerciseFactory.build(
            workout=workout,
            exercise=exercise,
            order=1,
        )
        with pytest.raises(ValidationError):
            duplicate.full_clean()

    def test_str_includes_exercise_name_and_slot(self, workout, exercise):
        we = WorkoutExerciseFactory(workout=workout, exercise=exercise, order=2)
        result = str(we)
        assert "Barbell Back Squat" in result
        assert "slot 2" in result


# ─── WorkoutSet ───────────────────────────────────────────────────────────────


class TestWorkoutSet:

    def test_reps_prescribed_zero_is_invalid(self, workout_exercise):
        ws = WorkoutSetFactory.build(
            workout_exercise=workout_exercise,
            reps_prescribed=0,
        )
        with pytest.raises(
            ValidationError, match="reps_prescribed must be greater than 0"
        ):
            ws.full_clean()

    def test_weight_prescribed_negative_is_invalid(self, workout_exercise):
        ws = WorkoutSetFactory.build(
            workout_exercise=workout_exercise,
            weight_prescribed=Decimal("-1.00"),
        )
        with pytest.raises(
            ValidationError, match="weight_prescribed cannot be negative"
        ):
            ws.full_clean()

    def test_weight_prescribed_zero_is_valid(self, workout_exercise):
        # bodyweight exercises have no load
        ws = WorkoutSetFactory(
            workout_exercise=workout_exercise,
            weight_prescribed=Decimal("0.00"),
            set_order=2,
        )
        assert ws.weight_prescribed == Decimal("0.00")

    def test_set_order_must_be_unique_within_exercise(self, workout_exercise):
        WorkoutSetFactory(workout_exercise=workout_exercise, set_order=1)
        duplicate = WorkoutSetFactory.build(
            workout_exercise=workout_exercise,
            set_order=1,
        )
        with pytest.raises(ValidationError):
            duplicate.full_clean()

    def test_valid_set_saves_successfully(self, workout_exercise):
        ws = WorkoutSetFactory(
            workout_exercise=workout_exercise,
            set_order=1,
            reps_prescribed=8,
            weight_prescribed=Decimal("80.00"),
        )
        assert ws.pk is not None
