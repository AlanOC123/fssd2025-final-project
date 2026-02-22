from django.core.exceptions import ValidationError
from django.db import models

from apps.exercises.models import Exercise
from apps.programs.models import ProgramPhase
from core.models import ApexModel


class Workout(ApexModel):
    """
    Base Workout model. Must be attached to a program phase
    """

    workout_name = models.CharField(max_length=300)
    estimated_duration_s = models.IntegerField()
    scheduled_for = models.DateField(blank=True, null=True)
    trainer_notes = models.TextField(max_length=500, blank=True)

    program_phase = models.ForeignKey(
        to=ProgramPhase, on_delete=models.CASCADE, related_name="workouts"
    )

    def __str__(self) -> str:
        return self.workout_name


class WorkoutExercise(ApexModel):
    """
    Workout component. Enables a structured routine to the user.
    Also used for logic engine calculations
    """

    sets_prescribed = models.SmallIntegerField()
    order = models.IntegerField()

    workout = models.ForeignKey(
        to=Workout, on_delete=models.CASCADE, related_name="exercises"
    )

    exercise = models.ForeignKey(
        to=Exercise, on_delete=models.PROTECT, related_name="workouts"
    )

    def __str__(self) -> str:
        return f"{self.exercise} -> {self.workout}"


class WorkoutSet(ApexModel):
    """
    Active set. Determined by trainer. Relates back to a workout exercise.
    Tracks order and presribed reps and weight.
    """

    reps_prescribed = models.SmallIntegerField()
    weight_prescribed = models.DecimalField(max_digits=5, decimal_places=2)
    set_order = models.SmallIntegerField()

    workout_exercise = models.ForeignKey(
        to=WorkoutExercise, on_delete=models.CASCADE, related_name="sets"
    )

    def __str__(self) -> str:
        return f"Set {self.set_order} of {self.workout_exercise.sets_prescribed}"


class WorkoutCompletionRecord(ApexModel):
    time_taken_s = models.IntegerField()
    completed_at = models.DateTimeField(blank=True, null=True)
    is_skipped = models.BooleanField(default=False)

    workout = models.OneToOneField(
        to=Workout, on_delete=models.CASCADE, related_name="completion_record"
    )

    def clean(self):
        if self.is_skipped and self.time_taken_s > 0:
            raise ValidationError("A skipped workout cannot have a time taken metric")
        return super().clean()

    def save(self, *args, **kwargs):
        self.clean()
        super().save(*args, **kwargs)

    def __str__(self) -> str:
        return f"Workout completion record for {self.workout}"


class WorkoutExerciseCompletionRecord(ApexModel):
    """
    Record a workout exercise. Trackes in progress completions of client exercises.
    """

    workout_completion_record = models.ForeignKey(
        to=WorkoutCompletionRecord,
        on_delete=models.CASCADE,
        related_name="exercise_records",
        null=True,
    )

    workout_exercise = models.OneToOneField(
        to=WorkoutExercise, on_delete=models.CASCADE, related_name="completion_record"
    )

    completed_at = models.DateTimeField(blank=True, null=True)
    is_skipped = models.BooleanField(default=False)

    difficulty_rating = models.SmallIntegerField(blank=True, null=True)

    def clean(self):
        if (
            self.workout_completion_record.id
            and self.workout_completion_record.is_skipped
        ):
            raise ValidationError("A skipped workout cannot have associated exercises")
        return super().clean()

    def __str__(self):
        return f"Completion record of {self.workout_exercise.exercise}"


class WorkoutSetCompletionRecord(ApexModel):
    """
    Recording of the sets by the client.
    Used to check for immediate and historical changes.
    """

    reps_completed = models.SmallIntegerField()
    weight_completed = models.DecimalField(max_digits=5, decimal_places=2)
    completed_at = models.DateTimeField(blank=True, null=True)
    is_skipped = models.BooleanField(default=False)

    workout_set = models.OneToOneField(
        to=WorkoutSet, on_delete=models.CASCADE, related_name="completion_record"
    )

    exercise_completion_record = models.ForeignKey(
        to=WorkoutExerciseCompletionRecord,
        on_delete=models.CASCADE,
        related_name="completed_sets",
    )

    reps_in_reserve = models.SmallIntegerField(blank=True, null=True)

    def __str__(self):
        return f"Set completion record of set {self.workout_set.set_order}"
