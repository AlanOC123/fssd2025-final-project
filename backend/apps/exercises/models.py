from django.core.exceptions import ValidationError
from django.db import models

from apps.biology.models import JointAction
from apps.users.models import ExperienceLevel
from core.models import ApexModel, NormalisedLookupModel


class JointRangeOfMotion(NormalisedLookupModel):
    """Represents the range of motion for a joint during an exercise.

    Attributes:
        impact_factor: A decimal representing the relative impact or load intensity.
    """

    impact_factor = models.DecimalField(max_digits=3, decimal_places=2)

    class Meta:
        verbose_name_plural = "Joint Ranges of Motion"
        ordering = ["-impact_factor"]


class ExercisePhase(NormalisedLookupModel):
    """Represents a specific phase of an exercise (e.g., Eccentric, Concentric)."""

    class Meta:
        verbose_name_plural = "Exercise Phases"


class Equipment(NormalisedLookupModel):
    """Represents the physical equipment required to perform an exercise."""

    class Meta:
        verbose_name_plural = "Equipment"


class Exercise(ApexModel):
    """Core exercise model containing descriptive data and metadata.

    The api_name attribute must match the Ninja API naming convention for
    external synchronization.

    Attributes:
        exercise_name: Unique display name of the exercise.
        api_name: Unique identifier used for API integrations.
        equipment: Many-to-many relationship with Equipment models.
        experience_level: Foreign key to user ExperienceLevel.
        instructions: Detailed steps for performing the exercise.
        safety_tips: Precautions to avoid injury.
        is_enriched: Boolean flag indicating if instructions and safety tips are present.
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
        """Validates that enriched exercises contain required content.

        Raises:
            ValidationError: If is_enriched is True but instructions or
                safety_tips are missing.
        """
        super().clean()

        if self.is_enriched and (not self.instructions or not self.safety_tips):
            raise ValidationError(
                {
                    "is_enriched": "Enriched exercises must include instructions and safety_tips."
                }
            )

    def save(self, *args, **kwargs):
        """Updates enrichment status and performs full validation before saving."""
        self.is_enriched = bool(self.instructions and self.safety_tips)

        self.full_clean()
        super().save(*args, **kwargs)

    def __str__(self) -> str:
        return self.exercise_name


class ExerciseMovement(ApexModel):
    """Relates an exercise to its constituent movement phases.

    Attributes:
        phase: The specific movement phase (e.g., Concentric).
        exercise: The exercise this movement belongs to.
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
    """Maps specific joint actions and ranges of motion to an exercise movement.

    This model enables granular tracking of muscle load and partial loading
    calculations based on the specific range of motion involved in a movement.

    Attributes:
        joint_action: The anatomical action occurring at the joint.
        joint_range_of_motion: The extent of the movement.
        exercise_movement: The specific phase/movement being described.
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
