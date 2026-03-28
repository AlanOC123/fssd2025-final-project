from django.db import models

from apps.exercises.models import Exercise
from apps.programs.models import Program
from apps.workouts.models import WorkoutCompletionRecord
from core.models import ApexModel


class ExerciseSessionSnapshot(ApexModel):
    """Model representing a point-in-time analytical capture of an exercise session.

    This class stores computed metrics such as estimated one-rep max (1RM),
    actual session load, and theoretical target loads. It serves as a
    historical record for progression analysis and load distribution tracking.

    Attributes:
        program: The training program associated with the snapshot.
        exercise: The specific exercise being analyzed.
        session: The workout completion record that triggered the snapshot.
        one_rep_max: The estimated 1RM calculated from the session's performance.
        session_load: The total volume or load achieved during the session.
        target_load: The theoretical load the user was expected to achieve.
        weight_floor: The calculated minimum weight recommended for the session.
        weight_ceiling: The calculated maximum weight recommended for the session.
        computed_at: The timestamp indicating when these metrics were generated.
    """

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
        """Metadata for the ExerciseSessionSnapshot model."""

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
        """Returns a human-readable identifier for the snapshot.

        Returns:
            str: A formatted string identifying the exercise, program, and session.
        """
        return (
            f"Snapshot: {self.exercise.exercise_name} "
            f"in {self.program.program_name} "
            f"@ session {self.session_id}"
        )
