from decimal import Decimal

from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from django.db import models

from apps.exercises.models import Exercise
from apps.programs.models import ProgramPhase
from core.models import ApexModel

User = get_user_model()


class Workout(ApexModel):
    """A trainer-authored workout attached to a program phase.

    Immutable once the phase is COMPLETED or ABANDONED — enforced by the service,
    not the model.

    Attributes:
        workout_name: The descriptive name of the workout.
        planned_date: The date the workout is scheduled to occur.
        program_phase: Foreign key to the associated ProgramPhase.
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
    """An ordered exercise slot within a workout.

    sets_prescribed drives how many WorkoutSet rows the trainer creates.

    Attributes:
        exercise: Foreign key to the Exercise definition.
        workout: Foreign key to the parent Workout.
        order: The sequence of the exercise within the workout.
        sets_prescribed: The number of sets the trainer intends for this exercise.
        trainer_notes: Optional instructions provided by the trainer.
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
        """Validates that prescribed sets are positive.

        Raises:
            ValidationError: If sets_prescribed is less than or equal to 0.
        """
        super().clean()
        if self.sets_prescribed <= 0:
            raise ValidationError("sets_prescribed must be greater than 0.")

    def save(self, *args, **kwargs):
        """Performs full validation before saving the instance."""
        self.full_clean()
        return super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.exercise.exercise_name} (slot {self.order}) in {self.workout.workout_name}"


class WorkoutSet(ApexModel):
    """A single prescribed set within a workout exercise.

    Represents the trainer's target — the completion record tracks what actually happened.

    Attributes:
        workout_exercise: Foreign key to the parent WorkoutExercise.
        set_order: The sequence of the set within the exercise.
        reps_prescribed: Target number of repetitions.
        weight_prescribed: Target weight for the set.
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
        """Validates prescriptions for reps and weight.

        Raises:
            ValidationError: If reps_prescribed is not positive or weight is negative.
        """
        super().clean()
        if self.reps_prescribed <= 0:
            raise ValidationError("reps_prescribed must be greater than 0.")
        if self.weight_prescribed < Decimal("0.00"):
            raise ValidationError("weight_prescribed cannot be negative.")

    def save(self, *args, **kwargs):
        """Performs full validation before saving the instance."""
        self.full_clean()
        return super().save(*args, **kwargs)

    def __str__(self):
        return f"Set {self.set_order} of {self.workout_exercise}"


class WorkoutCompletionRecord(ApexModel):
    """Record created when a client starts or skips a workout.

    Acts as the session root — all exercise and set records hang off this.
    Terminal skip: if is_skipped=True, no ExerciseCompletionRecords should exist.

    Attributes:
        workout: One-to-one link to the prescribed Workout.
        client: Foreign key to the User performing the workout.
        is_skipped: Boolean indicating if the workout was bypassed.
        started_at: Timestamp for the start of the session.
        completed_at: Optional timestamp for when the session ended.
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
        """Ensures chronological consistency between start and completion.

        Raises:
            ValidationError: If completed_at occurs before started_at.
        """
        super().clean()
        if (
            self.completed_at
            and self.started_at
            and self.completed_at < self.started_at
        ):
            raise ValidationError("completed_at cannot be before started_at.")

    def save(self, *args, **kwargs):
        """Performs full validation before saving the instance."""
        self.full_clean()
        return super().save(*args, **kwargs)

    @property
    def duration_s(self):
        """Calculates the total duration of the workout in seconds.

        Returns:
            int: The duration in seconds, or None if completion time is missing.
        """
        if self.started_at and self.completed_at:
            return int((self.completed_at - self.started_at).total_seconds())
        return None

    def __str__(self):
        return f"Session: {self.workout.workout_name} ({self.client.email})"


class WorkoutExerciseCompletionRecord(ApexModel):
    """Record created when a client starts or skips an exercise.

    Terminal skip: if is_skipped=True, no SetCompletionRecords should exist.

    Attributes:
        workout_completion_record: Foreign key to the parent session record.
        workout_exercise: One-to-one link to the prescribed WorkoutExercise.
        is_skipped: Boolean indicating if the exercise was bypassed.
        started_at: Timestamp for the start of the exercise.
        completed_at: Optional timestamp for when the exercise ended.
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
        """Ensures chronological consistency between start and completion.

        Raises:
            ValidationError: If completed_at occurs before started_at.
        """
        super().clean()
        if (
            self.completed_at
            and self.started_at
            and self.completed_at < self.started_at
        ):
            raise ValidationError("completed_at cannot be before started_at.")

    def save(self, *args, **kwargs):
        """Performs full validation before saving the instance."""
        self.full_clean()
        return super().save(*args, **kwargs)

    def __str__(self):
        return f"Exercise record: {self.workout_exercise} in session {self.workout_completion_record_id}"


class WorkoutSetCompletionRecord(ApexModel):
    """The atomic unit of completion data for a single set.

    Stores actual performance metrics vs prescribed targets.

    Attributes:
        exercise_completion_record: Foreign key to the parent exercise record.
        workout_set: One-to-one link to the prescribed WorkoutSet.
        is_skipped: Boolean indicating if the set was bypassed.
        completed_at: Timestamp for when the set was finished.
        reps_completed: Actual number of repetitions performed.
        weight_completed: Actual weight used for the set.
        difficulty_rating: Client-reported RPE or difficulty (1-10).
        reps_in_reserve: Client-reported repetitions left in the tank.
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
        """Validates performance metrics and metadata.

        Validates that completed sets have positive reps, non-negative weight,
        a timestamp, and that subjective ratings are within valid ranges.

        Raises:
            ValidationError: If performance metrics are invalid or ratings
                are out of bounds.
        """
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
        """Performs full validation before saving the instance."""
        self.full_clean()
        return super().save(*args, **kwargs)

    @property
    def reps_diff(self):
        """Calculates difference between actual and prescribed reps.

        Returns:
            int: The difference in reps, or None if skipped.
        """
        if self.is_skipped:
            return None
        return self.reps_completed - self.workout_set.reps_prescribed

    @property
    def weight_diff(self):
        """Calculates difference between actual and prescribed weight.

        Returns:
            Decimal: The weight difference, or None if skipped.
        """
        if self.is_skipped:
            return None
        return self.weight_completed - self.workout_set.weight_prescribed

    def __str__(self):
        return f"Set record: {self.workout_set} ({'skipped' if self.is_skipped else 'completed'})"
