from django.core.exceptions import ValidationError
from django.db import models

from apps.biology.models import JointAction
from apps.users.models import ExperienceLevel
from core.models import ApexModel, NormalisedLookupModel


class JointRangeOfMotion(NormalisedLookupModel):
    impact_factor = models.DecimalField(max_digits=3, decimal_places=2)

    class Meta:
        verbose_name_plural = "Joint Ranges of Motion"
        ordering = ["-impact_factor"]


class ExercisePhase(NormalisedLookupModel):
    class Meta:
        verbose_name_plural = "Exercise Phases"


class Equipment(NormalisedLookupModel):
    class Meta:
        verbose_name_plural = "Equipment"


class Exercise(ApexModel):
    """
    Core exercise model.
    Name must match Ninja API naming convention for API call.
    """

    exercise_name = models.CharField(max_length=100, unique=True)
    api_name = models.CharField(max_length=100, unique=True)
    equipment = models.ManyToManyField(
        to=Equipment, related_name="exercises", blank=True
    )
    experience_level = models.ForeignKey(
        to=ExperienceLevel, on_delete=models.CASCADE, related_name="exercises"
    )
    instructions = models.TextField(blank=True)
    safety_tips = models.TextField(blank=True)
    is_enriched = models.BooleanField(default=False)

    class Meta:
        verbose_name_plural = "Exercises"
        ordering = ["exercise_name"]

    def clean(self):
        super().clean()

        if self.is_enriched and (not self.instructions or not self.safety_tips):
            raise ValidationError(
                {
                    "is_enriched": "Enriched exercises must include instructions and safety_tips."
                }
            )

    def save(self, *args, **kwargs):
        self.is_enriched = bool(self.instructions and self.safety_tips)

        self.full_clean()
        super().save(*args, **kwargs)

    def __str__(self) -> str:
        return self.exercise_name


class ExerciseMovement(ApexModel):
    """
    Breakdown of exercises into its individual movements.
    """

    phase = models.ForeignKey(
        to=ExercisePhase, on_delete=models.CASCADE, related_name="exercise_movements"
    )

    exercise = models.ForeignKey(
        to=Exercise, on_delete=models.CASCADE, related_name="exercise_movements"
    )

    class Meta:
        verbose_name_plural = "Exercise Movements"
        constraints = [
            models.UniqueConstraint(
                fields=["phase", "exercise"], name="unique_phase_per_exercise_movement"
            )
        ]

        ordering = ["phase__code"]

    def __str__(self) -> str:
        return f"{self.phase.label} of {self.exercise.exercise_name}"


class JointContribution(ApexModel):
    """
    Allows accurate tracking of load across exercise movements.
    Enables partial loading of movement given range of motion
    """

    joint_action = models.ForeignKey(
        to=JointAction, on_delete=models.CASCADE, related_name="exercise_contributions"
    )

    joint_range_of_motion = models.ForeignKey(
        to=JointRangeOfMotion,
        on_delete=models.CASCADE,
        related_name="exercise_contributions",
    )

    exercise_movement = models.ForeignKey(
        to=ExerciseMovement,
        on_delete=models.CASCADE,
        related_name="joint_contributions",
    )

    class Meta:
        verbose_name_plural = "Joint Contributions"
        constraints = [
            models.UniqueConstraint(
                fields=["exercise_movement", "joint_action"],
                name="unique_exercise_movement_per_joint_action",
            )
        ]

        ordering = ["-joint_range_of_motion__impact_factor"]

    def __str__(self) -> str:
        return f"{self.exercise_movement} -> {self.joint_action}"
