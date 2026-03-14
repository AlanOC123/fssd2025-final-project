from django.db import models

from apps.biology.models import JointAction
from apps.users.models import ExperienceLevel
from core.models import ApexModel


class JointRangeOfMotion(ApexModel):
    """
    Describes the available range of motion and enables impact contribution factors.
    """

    range_of_motion_name = models.CharField(max_length=50, unique=True)
    impact_factor = models.DecimalField(max_digits=3, decimal_places=2)

    def __str__(self) -> str:
        return self.range_of_motion_name


class ExercisePhase(ApexModel):
    """
    Describes the available phases of a movement
    """

    phase_name = models.CharField(max_length=50, unique=True)

    def __str__(self) -> str:
        return self.phase_name


class Equipment(ApexModel):
    """
    Table to serialise equipment.
    Equipment name gained from call to Ninja API.
    """

    equipment_name = models.TextField(max_length=100, unique=True)

    def __str__(self) -> str:
        return self.equipment_name


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
        unique_together = ("exercise", "phase")

    def __str__(self) -> str:
        return f"{self.phase.phase_name} of {self.exercise.exercise_name}"


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
        unique_together = ("exercise_movement", "joint_action")
        ordering = ["-joint_range_of_motion__impact_factor"]

    def __str__(self) -> str:
        return f"{self.exercise_movement} -> {self.joint_action}"
