from decimal import Decimal

from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from django.db import models

from apps.exercises.models import Exercise
from apps.programs.models import ProgramPhase
from core.models import ApexModel

User = get_user_model()


# Prescription Path


class Workout(ApexModel):
    """
    A trainer-authored workout attached to a program phase.
    Immutable once the phase is COMPLETED or ABANDONED — enforced by the service,
    not the model.
    """

    workout_name = models.CharField(max_length=300)
    planned_date = models.DateField(blank=True, null=True)

    program_phase = models.ForeignKey(
        to=ProgramPhase,
        on_delete=models.CASCADE,
        related_name="workouts",
    )

    class Meta:
        ordering = ["planned_date"]

    def __str__(self):
        return self.workout_name


class WorkoutExercise(ApexModel):
    """
    An ordered exercise slot within a workout.
    sets_prescribed drives how many WorkoutSet rows the trainer creates.
    """

    exercise = models.ForeignKey(
        to=Exercise,
        on_delete=models.PROTECT,
        related_name="workout_exercises",
    )

    workout = models.ForeignKey(
        to=Workout,
        on_delete=models.CASCADE,
        related_name="exercises",
    )

    order = models.PositiveSmallIntegerField()
    sets_prescribed = models.PositiveSmallIntegerField()
    trainer_notes = models.TextField(max_length=500, blank=True)

    class Meta:
        ordering = ["order"]
        constraints = [
            models.UniqueConstraint(
                fields=["workout", "order"],
                name="unique_exercise_order_per_workout",
            )
        ]

    def clean(self):
        super().clean()
        if self.sets_prescribed <= 0:
            raise ValidationError("sets_prescribed must be greater than 0.")

    def save(self, *args, **kwargs):
        self.full_clean()
        return super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.exercise.exercise_name} (slot {self.order}) in {self.workout.workout_name}"


class WorkoutSet(ApexModel):
    """
    A single prescribed set within a workout exercise.
    Represents the trainer's target — the completion record tracks what actually happened.
    """

    workout_exercise = models.ForeignKey(
        to=WorkoutExercise,
        on_delete=models.CASCADE,
        related_name="sets",
    )

    set_order = models.PositiveSmallIntegerField()
    reps_prescribed = models.PositiveSmallIntegerField()
    weight_prescribed = models.DecimalField(max_digits=6, decimal_places=2)

    class Meta:
        ordering = ["set_order"]
        constraints = [
            models.UniqueConstraint(
                fields=["workout_exercise", "set_order"],
                name="unique_set_order_per_exercise",
            )
        ]

    def clean(self):
        super().clean()
        if self.reps_prescribed <= 0:
            raise ValidationError("reps_prescribed must be greater than 0.")
        if self.weight_prescribed < Decimal("0.00"):
            raise ValidationError("weight_prescribed cannot be negative.")

    def save(self, *args, **kwargs):
        self.full_clean()
        return super().save(*args, **kwargs)

    def __str__(self):
        return f"Set {self.set_order} of {self.workout_exercise}"


# Completion Path


class WorkoutCompletionRecord(ApexModel):
    """
    Created when a client starts or skips a workout. Acts as the session root —
    all exercise and set records hang off this.

    Terminal skip: if is_skipped=True, no ExerciseCompletionRecords should exist.
    Enforced by the service, not the model.
    """

    workout = models.OneToOneField(
        to=Workout,
        on_delete=models.CASCADE,
        related_name="completion_record",
    )

    client = models.ForeignKey(
        to=User,
        on_delete=models.CASCADE,
        related_name="workout_completion_records",
    )

    is_skipped = models.BooleanField(default=False)

    started_at = models.DateTimeField()
    completed_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        ordering = ["started_at"]

    def clean(self):
        super().clean()
        if (
            self.completed_at
            and self.started_at
            and self.completed_at < self.started_at
        ):
            raise ValidationError("completed_at cannot be before started_at.")

    def save(self, *args, **kwargs):
        self.full_clean()
        return super().save(*args, **kwargs)

    @property
    def duration_s(self):
        if self.started_at and self.completed_at:
            return int((self.completed_at - self.started_at).total_seconds())
        return None

    def __str__(self):
        return f"Session: {self.workout.workout_name} ({self.client.email})"


class WorkoutExerciseCompletionRecord(ApexModel):
    """
    Created when a client starts or skips an exercise during a session.

    Terminal skip: if is_skipped=True, no SetCompletionRecords should exist.
    Enforced by the service, not the model.
    """

    workout_completion_record = models.ForeignKey(
        to=WorkoutCompletionRecord,
        on_delete=models.CASCADE,
        related_name="exercise_records",
    )

    workout_exercise = models.OneToOneField(
        to=WorkoutExercise,
        on_delete=models.CASCADE,
        related_name="completion_record",
    )

    is_skipped = models.BooleanField(default=False)
    started_at = models.DateTimeField()
    completed_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        ordering = ["started_at"]

    def clean(self):
        super().clean()
        if (
            self.completed_at
            and self.started_at
            and self.completed_at < self.started_at
        ):
            raise ValidationError("completed_at cannot be before started_at.")

    def save(self, *args, **kwargs):
        self.full_clean()
        return super().save(*args, **kwargs)

    def __str__(self):
        return f"Exercise record: {self.workout_exercise} in session {self.workout_completion_record_id}"


class WorkoutSetCompletionRecord(ApexModel):
    """
    The atomic unit of completion data. Created per set as the client works through
    an exercise. Stores actual vs prescribed for diff calculations.

    reps_completed and weight_completed are 0 when is_skipped=True — use
    is_skipped as the authoritative signal, not zero values.
    """

    exercise_completion_record = models.ForeignKey(
        to=WorkoutExerciseCompletionRecord,
        on_delete=models.CASCADE,
        related_name="set_records",
    )

    workout_set = models.OneToOneField(
        to=WorkoutSet,
        on_delete=models.CASCADE,
        related_name="completion_record",
    )

    is_skipped = models.BooleanField(default=False)
    completed_at = models.DateTimeField(null=True, blank=True)

    reps_completed = models.PositiveSmallIntegerField(default=0)
    weight_completed = models.DecimalField(
        max_digits=6, decimal_places=2, default=Decimal("0.00")
    )

    difficulty_rating = models.PositiveSmallIntegerField(null=True, blank=True)
    reps_in_reserve = models.PositiveSmallIntegerField(null=True, blank=True)

    class Meta:
        ordering = ["workout_set__set_order"]

    def clean(self):
        super().clean()
        if not self.is_skipped:
            if self.reps_completed <= 0:
                raise ValidationError(
                    "reps_completed must be greater than 0 for a completed set."
                )
            if self.weight_completed < Decimal("0.00"):
                raise ValidationError("weight_completed cannot be negative.")
            if self.completed_at is None:
                raise ValidationError(
                    "A completed set must have a completed_at timestamp."
                )
        if self.difficulty_rating is not None and not (
            1 <= self.difficulty_rating <= 10
        ):
            raise ValidationError("difficulty_rating must be between 1 and 10.")
        if self.reps_in_reserve is not None and self.reps_in_reserve < 0:
            raise ValidationError("reps_in_reserve cannot be negative.")

    def save(self, *args, **kwargs):
        self.full_clean()
        return super().save(*args, **kwargs)

    @property
    def reps_diff(self):
        if self.is_skipped:
            return None
        return self.reps_completed - self.workout_set.reps_prescribed

    @property
    def weight_diff(self):
        if self.is_skipped:
            return None
        return self.weight_completed - self.workout_set.weight_prescribed

    def __str__(self):
        return f"Set record: {self.workout_set} ({'skipped' if self.is_skipped else 'completed'})"
