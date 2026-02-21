from django.db import models

from apps.users.models import ExperienceLevel, TrainerClientMembership, TrainingGoal
from core.models import ApexModel


class ProgramPhaseOption(ApexModel):
    """
    Table to record the different types of phases.
    Provides a consistent interface for trainer to program for clients
    """

    phase_name = models.CharField(max_length=150, unique=True)
    order_index = models.SmallIntegerField(unique=True)
    default_duration = models.SmallIntegerField(default=4)
    description = models.TextField(max_length=500)

    class Meta:
        verbose_name = "Program Phase Options"
        ordering = ["order_index"]

    def __str__(self) -> str:
        return self.phase_name


class Program(ApexModel):
    """
    Actual program that trainers will create for a client.
    Consists of phases.
    Must be related to an active client trainer membership
    """

    program_name = models.CharField(max_length=150)

    trainer_client_membership = models.ForeignKey(
        to=TrainerClientMembership,
        on_delete=models.SET_NULL,
        related_name="programs",
        null=True,
    )

    trainer_goal = models.ForeignKey(
        to=TrainingGoal, related_name="programs", on_delete=models.PROTECT
    )

    experience_level = models.ForeignKey(
        to=ExperienceLevel, on_delete=models.PROTECT, related_name="programs"
    )

    @property
    def calculated_duration(self):
        """
        Calculated property. Calculates the total duration of the program based.
        Check first if a custom duration is set.
        If not (equals 0) then use the default duration accessing phase options
        """

        total = self.phases.aggregate(
            total_time=models.Sum(
                models.Case(
                    models.When(
                        custom_duration__gt=0, then=models.F("custom_duration")
                    ),
                    models.When(
                        phase_option__default_duration__gt=0,
                        then=models.F("phase_option__default_duration"),
                    ),
                    default=0,
                    output_field=models.IntegerField(),
                )
            )
        )["total_time"]

        return total or 0

    def __str__(self) -> str:
        if self.trainer_client_membership:
            client_name = self.trainer_client_membership.client.user.first_name
            trainer_name = self.trainer_client_membership.trainer.user.first_name
            return f"{self.program_name} for {client_name} by {trainer_name}"
        return f"{self.program_name} (Archived/Detached)"


class ProgramPhase(ApexModel):
    """
    Specific phase the program is currently in.
    Links to the abstract Phase options table where meta data is located.
    """

    phase_option = models.ForeignKey(
        to=ProgramPhaseOption, on_delete=models.PROTECT, related_name="phases"
    )

    program = models.ForeignKey(
        to=Program, on_delete=models.CASCADE, related_name="phases"
    )

    is_active = models.BooleanField(default=False)

    is_completed = models.BooleanField(default=False)

    completed_at = models.DateTimeField(null=True, blank=True)

    custom_duration = models.SmallIntegerField(default=0)

    def __str__(self) -> str:
        return f"{self.phase_option.phase_name} of {self.program.program_name}"
