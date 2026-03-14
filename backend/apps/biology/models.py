from decimal import Decimal

from django.core.exceptions import ValidationError
from django.db import models

from core.models import ApexModel, NormalisedLookupModel


class PlaneOfMotion(NormalisedLookupModel):
    class Meta:
        verbose_name_plural = "Planes of Motion"


class AnatomicalDirection(NormalisedLookupModel):
    class Meta:
        verbose_name_plural = "Anatomical Directions"


class MovementPattern(NormalisedLookupModel):
    class Meta:
        verbose_name_plural = "Movement Patterns"


class MuscleRole(NormalisedLookupModel):
    class Meta:
        verbose_name_plural = "Muscle Roles"


class Joint(NormalisedLookupModel):
    class Meta:
        verbose_name_plural = "Joints"


class MuscleGroup(NormalisedLookupModel):
    class Meta:
        verbose_name_plural = "Muscle Groups"


class Muscle(NormalisedLookupModel):
    """
    Table to list muscle names.
    Allows tracking of load and complex relations back to joints.
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
    """
    Represents a specific movement a joint can perform.
    Each joint can only have one entry per movement pattern.
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
        return f"{self.joint.code} {self.movement.code}"


class MuscleInvolvement(ApexModel):
    """
    Weighted relationship between a muscle and a joint action.

    impact_factor expresses relative contribution of the muscle
    in the action (0.00–1.00). Used later for load distribution
    calculations in training analysis.
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
        return f"{self.muscle} -> {self.joint_action}"

    class Meta:
        ordering = ["-impact_factor"]
        constraints = [
            models.UniqueConstraint(
                name="unique_muscle_joint_action", fields=["muscle", "joint_action"]
            )
        ]

    def clean(self) -> None:
        super().clean()

        if self.impact_factor is None:
            raise ValidationError("Missing impact factor")

        if self.impact_factor < Decimal("0.00") or self.impact_factor > Decimal("1.00"):
            raise ValidationError("Impact factor must be between 0.00 and 1.00")

    def save(self, *args, **kwargs):
        self.full_clean()
        return super().save(*args, **kwargs)
