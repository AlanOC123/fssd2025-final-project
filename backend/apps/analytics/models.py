from decimal import Decimal

from django.db import models

from apps.exercises.models import Exercise
from apps.programs.models import Program
from apps.workouts.models import WorkoutCompletionRecord
from core.models import ApexModel


class ExerciseSessionSnapshot(ApexModel):
    program = models.ForeignKey(
        to=Program,
        on_delete=models.CASCADE,
        related_name="exercise_snapshots",
    )

    exercise = models.ForeignKey(
        to=Exercise,
        on_delete=models.PROTECT,
        related_name="session_snapshots",
    )

    session = models.ForeignKey(
        to=WorkoutCompletionRecord,
        on_delete=models.CASCADE,
        related_name="exercise_snapshots",
    )

    one_rep_max = models.DecimalField(
        max_digits=6,
        decimal_places=2,
    )

    session_load = models.DecimalField(
        max_digits=10,
        decimal_places=2,
    )

    target_load = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        null=True,
        blank=True,
    )

    weight_floor = models.DecimalField(
        max_digits=6,
        decimal_places=2,
        null=True,
        blank=True,
    )

    weight_ceiling = models.DecimalField(
        max_digits=6,
        decimal_places=2,
        null=True,
        blank=True,
    )

    computed_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["program", "exercise", "session"],
                name="unique_snapshot_per_exercise_per_session",
            )
        ]
        ordering = ["session__completed_at"]
        indexes = [
            models.Index(fields=["program", "exercise"]),
        ]

    def __str__(self):
        return (
            f"Snapshot: {self.exercise.exercise_name} "
            f"in {self.program.program_name} "
            f"@ session {self.session_id}"
        )
