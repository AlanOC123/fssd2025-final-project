from django.db import models

from core.models import ApexModel


class PlaneOfMotion(ApexModel):
    """
    Helper table for consistent planes of motion
    """

    plane_name = models.CharField(max_length=50, unique=True)

    def __str__(self) -> str:
        return self.plane_name


class AnatomicalDirection(ApexModel):
    """
    Helper table consistent anatomical directions
    """

    direction_name = models.CharField(max_length=50, unique=True)

    def __str__(self) -> str:
        return self.direction_name


class MovementPattern(ApexModel):
    """
    Helper table consistent movement patterns
    """

    pattern_name = models.CharField(max_length=100, unique=True)

    def __str__(self) -> str:
        return self.pattern_name


class MuscleRole(ApexModel):
    """
    Helper table consistent muscle roles names
    """

    role_name = models.CharField(max_length=50, unique=True)

    def __str__(self) -> str:
        return self.role_name


class Joint(ApexModel):
    """
    Main hook table for exercise biomechanics
    """

    joint_name = models.CharField(max_length=50, unique=True)

    def __str__(self) -> str:
        return self.joint_name


class JointAction(ApexModel):
    """
    Expands joints to make them actionable. Contains metadata about movement.
    Ensure uniqueness.
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
        unique_together = ("joint", "movement")

    def __str__(self) -> str:
        return f"{self.joint.joint_name} {self.movement.pattern_name}"


class Muscle(ApexModel):
    """
    Table to list muscle names.
    Allows tracking of load and complex relations back to joints.
    """

    muscle_name = models.CharField(max_length=100, unique=True)

    anatomical_direction = models.ForeignKey(
        to=AnatomicalDirection,
        on_delete=models.CASCADE,
        null=True,
        related_name="muscles",
    )

    def __str__(self) -> str:
        return self.muscle_name


class MuscleInvolvement(ApexModel):
    """
    Track muscle involments in enabling a joint action.
    Allows more complex load calculations.
    Ordered by impact factor.
    Enables unique muscle -> joint interactions.
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
        unique_together = ("muscle", "joint_action")
        ordering = ["-impact_factor"]
