from decimal import Decimal

from django.core.exceptions import ValidationError
from django.db import models

from core.models import ApexModel, NormalisedLookupModel


class PlaneOfMotion(NormalisedLookupModel):
    """Model representing anatomical planes of motion.

    Standard planes (e.g., Sagittal, Frontal, Transverse) used to categorize
    joint movements.
    """

    class Meta:
        verbose_name_plural = "Planes of Motion"


class AnatomicalDirection(NormalisedLookupModel):
    """Model representing anatomical directions and positions.

    Standard directions (e.g., Anterior, Posterior, Medial) used to locate
    muscles or landmarks.
    """

    class Meta:
        verbose_name_plural = "Anatomical Directions"


class MovementPattern(NormalisedLookupModel):
    """Model representing patterns of joint movement.

    Standard movements (e.g., Flexion, Extension, Abduction) regardless of
    the joint performing them.
    """

    class Meta:
        verbose_name_plural = "Movement Patterns"


class MuscleRole(NormalisedLookupModel):
    """Model representing the functional roles of muscles during movement.

    Roles include classifications such as Agonist, Antagonist, Synergist,
    and Fixator.
    """

    class Meta:
        verbose_name_plural = "Muscle Roles"


class Joint(NormalisedLookupModel):
    """Model representing specific anatomical joints.

    Examples include the Shoulder, Elbow, Hip, and Knee.
    """

    class Meta:
        verbose_name_plural = "Joints"


class MuscleGroup(NormalisedLookupModel):
    """Model representing broader muscle groups.

    Examples include Chest, Back, Quadriceps, and Core.
    """

    class Meta:
        verbose_name_plural = "Muscle Groups"


class Muscle(NormalisedLookupModel):
    """Model representing specific muscles and their anatomical classifications.

    This table allows for tracking individual muscles, their primary groups,
    and their relative positions via anatomical directions.

    Attributes:
        anatomical_direction: Optional reference to the muscle's position.
        muscle_group: Optional reference to the broader group the muscle
            belongs to.
    """

    anatomical_direction = models.ForeignKey(
        to=AnatomicalDirection,
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name="muscles",
    )

    muscle_group = models.ForeignKey(
        to=MuscleGroup,
        on_delete=models.CASCADE,
        related_name="muscles",
        null=True,
        blank=True,
    )

    class Meta:
        verbose_name_plural = "Muscles"


class JointAction(ApexModel):
    """Model representing a specific movement a joint can perform.

    Links a joint to a movement pattern and defines the plane of motion
    in which that specific action occurs.

    Attributes:
        joint: The anatomical joint involved.
        movement: The pattern of movement being performed.
        plane: The plane of motion in which the action occurs.
    """

    joint = models.ForeignKey(
        to=Joint, on_delete=models.CASCADE, related_name="actions"
    )

    movement = models.ForeignKey(
        to=MovementPattern, on_delete=models.CASCADE, related_name="joint_actions"
    )

    plane = models.ForeignKey(
        to=PlaneOfMotion, on_delete=models.CASCADE, related_name="joint_actions"
    )

    class Meta:
        constraints = [
            models.UniqueConstraint(
                name="unique_movement_per_joint", fields=["joint", "movement"]
            )
        ]

        verbose_name_plural = "Joint Actions"

    def __str__(self) -> str:
        """Returns a string representation of the joint and its movement."""
        return f"{self.joint.code} {self.movement.code}"


class MuscleInvolvement(ApexModel):
    """Model representing the weighted contribution of a muscle to a joint action.

    Defines how much a muscle contributes (impact_factor) to a specific
    JointAction and what role it plays.

    Attributes:
        muscle: The muscle involved in the action.
        joint_action: The joint action being contributed to.
        role: The functional role (Agonist, etc.) the muscle plays.
        impact_factor: A decimal (0.00-1.00) expressing the relative
            contribution of the muscle.
    """

    muscle = models.ForeignKey(
        to=Muscle, on_delete=models.CASCADE, related_name="actions"
    )

    joint_action = models.ForeignKey(
        to=JointAction, on_delete=models.CASCADE, related_name="muscles"
    )

    role = models.ForeignKey(
        to=MuscleRole, on_delete=models.CASCADE, related_name="muscles"
    )

    impact_factor = models.DecimalField(
        max_digits=3,
        decimal_places=2,
    )

    def __str__(self) -> str:
        """Returns a string representation of the muscle's involvement."""
        return f"{self.muscle} -> {self.joint_action}"

    class Meta:
        ordering = ["-impact_factor"]
        constraints = [
            models.UniqueConstraint(
                name="unique_muscle_joint_action", fields=["muscle", "joint_action"]
            )
        ]

    def clean(self) -> None:
        """Validates that the impact factor is within the logical 0.0 to 1.0 range.

        Raises:
            ValidationError: If impact_factor is missing or outside the range
                0.00 to 1.00.
        """
        super().clean()

        if self.impact_factor is None:
            raise ValidationError("Missing impact factor")

        if self.impact_factor < Decimal("0.00") or self.impact_factor > Decimal("1.00"):
            raise ValidationError("Impact factor must be between 0.00 and 1.00")

    def save(self, *args, **kwargs):
        """Performs full validation before saving the instance."""
        self.full_clean()
        return super().save(*args, **kwargs)
