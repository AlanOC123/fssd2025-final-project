import math

from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from django.db import models

from apps.users.models import (
    ExperienceLevel,
    TrainerClientMembership,
    TrainingGoal,
)
from core.models import ApexModel, NormalisedLookupModel

from .constants import ProgramPhaseStatusesVocabulary, ProgramStatusesVocabulary

User = get_user_model()


class ProgramPhaseOption(NormalisedLookupModel):
    """Table to record the different types of phases.

    Provides a consistent interface for trainers to program for clients.

    Attributes:
        default_duration_days: Default length of the phase in days.
    """

    default_duration_days = models.PositiveSmallIntegerField(default=28)

    @property
    def default_duration_weeks(self):
        """Calculates the default duration in weeks, rounding up."""
        return math.ceil(self.default_duration_days / 7)

    class Meta:
        """Metadata options for ProgramPhaseOption."""

        verbose_name_plural = "Program Phase Options"

    def clean(self) -> None:
        """Validates that the default duration is positive.

        Raises:
            ValidationError: If default_duration_days is 0 or less.
        """
        super().clean()

        if self.default_duration_days <= 0:
            raise ValidationError("Default durations must be greater than 0")

    def save(self, *args, **kwargs):
        """Validates the model before saving."""
        self.full_clean()
        return super().save(*args, **kwargs)


class ProgramStatusOption(NormalisedLookupModel):
    """Lookup table for program-level status options."""

    class Meta:
        """Metadata options for ProgramStatusOption."""

        verbose_name_plural = "Program Status Options"


class ProgramPhaseStatusOption(NormalisedLookupModel):
    """Lookup table for individual phase status options."""

    class Meta:
        """Metadata options for ProgramPhaseStatusOption."""

        verbose_name_plural = "Program Phase Status Options"


class Program(ApexModel):
    """Actual program that trainers create for a client.

    Consists of multiple phases and must be related to an active
    client-trainer membership.

    Attributes:
        program_name: Name of the training program.
        trainer_client_membership: Relationship to the client-trainer pair.
        training_goal: Primary objective of the program.
        experience_level: Intended difficulty level.
        status: Current lifecycle state of the program.
        created_by_trainer: User who initially created the program.
        last_edited_by: Last user to modify the record.
        version: Integer tracking the program iteration.
        submitted_for_review_at: Timestamp of review submission.
        reviewed_at: Timestamp of review completion.
        started_at: Timestamp when the program officially began.
        completed_at: Timestamp of successful completion.
        abandoned_at: Timestamp if the program was stopped prematurely.
        review_notes: Feedback from the review process.
        completion_notes: Summary notes upon finishing.
        abandonment_reason: Explanation for program abandonment.
    """

    program_name = models.CharField(max_length=150)

    trainer_client_membership = models.ForeignKey(
        to=TrainerClientMembership,
        on_delete=models.SET_NULL,
        related_name="programs",
        null=True,
    )

    training_goal = models.ForeignKey(
        to=TrainingGoal,
        related_name="programs",
        on_delete=models.PROTECT,
    )

    experience_level = models.ForeignKey(
        to=ExperienceLevel,
        on_delete=models.PROTECT,
        related_name="programs",
    )

    status = models.ForeignKey(
        to=ProgramStatusOption,
        on_delete=models.PROTECT,
        related_name="programs",
    )

    created_by_trainer = models.ForeignKey(
        to=User,
        on_delete=models.SET_NULL,
        related_name="created_programs",
        null=True,
    )

    last_edited_by = models.ForeignKey(
        to=User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="edited_programs",
    )

    version = models.PositiveIntegerField(default=1)

    submitted_for_review_at = models.DateTimeField(null=True, blank=True)
    reviewed_at = models.DateTimeField(null=True, blank=True)
    started_at = models.DateTimeField(null=True, blank=True)
    completed_at = models.DateTimeField(null=True, blank=True)
    abandoned_at = models.DateTimeField(null=True, blank=True)

    review_notes = models.TextField(max_length=500, blank=True)
    completion_notes = models.TextField(max_length=500, blank=True)
    abandonment_reason = models.CharField(max_length=200, blank=True)

    @property
    def program_duration_days(self):
        """Total duration of all phases in days."""
        return sum(phase.duration_days for phase in self.phases.all())

    @property
    def program_duration_weeks(self):
        """Total duration of all phases in weeks, rounded up."""
        return math.ceil(self.program_duration_days / 7)

    @property
    def has_created_phases(self):
        """Checks if the program has any associated phases."""
        return self.phases.exists()

    @property
    def number_of_completed_phases(self):
        """Counts how many phases are marked as COMPLETED."""
        return sum(
            phase.status.code == ProgramPhaseStatusesVocabulary.COMPLETED
            for phase in self.phases.all()
        )

    @property
    def number_of_skipped_phases(self):
        """Counts how many phases are marked as SKIPPED."""
        return sum(
            phase.status.code == ProgramPhaseStatusesVocabulary.SKIPPED
            for phase in self.phases.all()
        )

    @property
    def number_of_archived_phases(self):
        """Counts how many phases are marked as ARCHIVED."""
        return sum(
            phase.status.code == ProgramPhaseStatusesVocabulary.ARCHIVED
            for phase in self.phases.all()
        )

    @property
    def all_phases_finished(self):
        """Checks if every phase is in a finished state."""
        return all(
            phase.status.code in ProgramPhaseStatusesVocabulary.FINISHED_STATES
            for phase in self.phases.all()
        )

    @property
    def remaining_phases(self):
        """Returns a list of phases that are not yet finished."""
        return [
            phase
            for phase in self.phases.all()
            if phase.status.code not in ProgramPhaseStatusesVocabulary.FINISHED_STATES
        ]

    @property
    def planned_start_date(self):
        """Gets the planned start date of the first phase."""
        first_phase = self.phases.first()
        return first_phase.planned_start_date if first_phase else None

    @property
    def planned_end_date(self):
        """Gets the planned end date of the last phase."""
        last_phase = self.phases.last()
        return last_phase.planned_end_date if last_phase else None

    @property
    def actual_start_date(self):
        """Gets the recorded start date of the first chronological phase."""
        first_phase = self.phases.order_by("sequence_order").first()
        return first_phase.actual_start_date if first_phase else None

    @property
    def actual_end_date(self):
        """Gets the recorded end date of the last chronological phase."""
        last_phase = self.phases.order_by("sequence_order").last()
        return last_phase.actual_end_date if last_phase else None

    def clean(self):
        """Performs complex cross-field validation for the program lifecycle.

        Raises:
            ValidationError: If business rules for transitions, roles,
                or timestamps are violated.
        """
        super().clean()

        status_code = self.status.code

        if self.version <= 0:
            raise ValidationError(
                "Invalid version code. Must be a number greater than 0."
            )

        if self.created_by_trainer and not self.created_by_trainer.is_trainer:
            raise ValidationError("Only trainers can create programs.")

        if status_code in ProgramStatusesVocabulary.LIVE_STATES:
            if not self.created_by_trainer:
                raise ValidationError(
                    "Live programs must record the trainer who created them."
                )

            if not self.trainer_client_membership:
                raise ValidationError(
                    "Live programs must be attached to an active membership."
                )

        if self.trainer_client_membership:
            if not self.created_by_trainer:
                raise ValidationError(
                    "Programs attached to a membership must record the trainer who created them."
                )

            if self.created_by_trainer != self.trainer_client_membership.trainer.user:
                raise ValidationError(
                    "Only the trainer associated with the membership can create a program."
                )

            if (
                status_code in ProgramStatusesVocabulary.LIVE_STATES
                and not self.trainer_client_membership.is_active
            ):
                raise ValidationError(
                    "Live programs must be attached to an active membership."
                )

        if (
            status_code == ProgramStatusesVocabulary.CREATING
            and self.submitted_for_review_at
        ):
            raise ValidationError(
                "Draft programs cannot have a review submission timestamp."
            )

        if (
            status_code
            in {
                ProgramStatusesVocabulary.CREATING,
                ProgramStatusesVocabulary.REVIEW,
            }
            and self.reviewed_at
        ):
            raise ValidationError(
                "Programs cannot be reviewed before a review outcome is reached."
            )

        if (
            status_code in ProgramStatusesVocabulary.SUBMITTED_STATES
            and not self.submitted_for_review_at
        ):
            raise ValidationError(
                "Programs past draft state must record when they were submitted for review."
            )

        if (
            status_code in ProgramStatusesVocabulary.REVIEWED_STATES
            and not self.reviewed_at
        ):
            raise ValidationError(
                "Reviewed programs must record when review action occurred."
            )

        if (
            status_code in ProgramStatusesVocabulary.STARTED_STATES
            and not self.started_at
        ):
            raise ValidationError("Started programs must record when they began.")

        if status_code == ProgramStatusesVocabulary.COMPLETED and not self.completed_at:
            raise ValidationError(
                "Completed programs must record a completion timestamp."
            )

        if status_code == ProgramStatusesVocabulary.ABANDONED and not self.abandoned_at:
            raise ValidationError(
                "Abandoned programs must record an abandonment timestamp."
            )

        if self.completed_at and self.abandoned_at:
            raise ValidationError("Programs cannot be both completed and abandoned.")

        if self.completion_notes and not self.completed_at:
            raise ValidationError(
                "Programs with completion notes must record a completion time."
            )

        if self.abandonment_reason and not self.abandoned_at:
            raise ValidationError(
                "Programs with an abandonment reason must record when they were abandoned."
            )

        if self.completed_at and self.abandonment_reason:
            raise ValidationError(
                "Completed programs cannot have an abandonment reason."
            )

        if self.abandoned_at and self.completion_notes:
            raise ValidationError("Abandoned programs cannot have completion notes.")

    def save(self, *args, **kwargs):
        """Validates the model before saving."""
        self.full_clean()
        return super().save(*args, **kwargs)

    def __str__(self) -> str:
        if self.trainer_client_membership:
            client_name = self.trainer_client_membership.client.user.first_name
            trainer_name = self.trainer_client_membership.trainer.user.first_name
            return f"{self.program_name} for {client_name} by {trainer_name}"
        return f"{self.program_name} (Archived/Detached)"


class ProgramPhase(ApexModel):
    """Specific phase within a program lifecycle.

    Links to the abstract ProgramPhaseOption for metadata and tracks
    individual execution dates and statuses.

    Attributes:
        phase_option: Reference to the template/type of phase.
        phase_name: User-defined name for this specific phase.
        phase_goal: Stated objective for the phase.
        program: Parent training program.
        sequence_order: Positioning of the phase within the program.
        status: Lifecycle state of this specific phase.
        trainer_notes: Internal notes for the trainer.
        client_notes: Notes visible or relevant to the client.
        planned_start_date: Projected start.
        planned_end_date: Projected end.
        actual_start_date: Recorded day the phase started.
        actual_end_date: Recorded day the phase ended.
        started_at: High-precision timestamp of start.
        completed_at: High-precision timestamp of completion.
        created_by_trainer: User who created the phase.
        last_edited_by: User who last modified the phase.
        skipped_at: Timestamp if skipped.
        skipped_reason: Reason for skipping.
        archived_at: Timestamp if archived.
        archived_reason: Reason for archiving.
    """

    phase_option = models.ForeignKey(
        to=ProgramPhaseOption,
        on_delete=models.PROTECT,
        related_name="phases",
    )

    phase_name = models.CharField(max_length=120, blank=True)
    phase_goal = models.CharField(max_length=200, blank=True)

    program = models.ForeignKey(
        to=Program,
        on_delete=models.CASCADE,
        related_name="phases",
    )

    sequence_order = models.PositiveSmallIntegerField(default=1)

    status = models.ForeignKey(
        to=ProgramPhaseStatusOption,
        on_delete=models.PROTECT,
        related_name="program_phases",
    )

    trainer_notes = models.TextField(max_length=500, blank=True)
    client_notes = models.TextField(max_length=500, blank=True)

    planned_start_date = models.DateField()
    planned_end_date = models.DateField()

    actual_start_date = models.DateField(null=True, blank=True)
    actual_end_date = models.DateField(null=True, blank=True)

    started_at = models.DateTimeField(null=True, blank=True)
    completed_at = models.DateTimeField(null=True, blank=True)

    created_by_trainer = models.ForeignKey(
        to=User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="created_program_phases",
    )

    last_edited_by = models.ForeignKey(
        to=User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="edited_program_phases",
    )

    skipped_at = models.DateTimeField(null=True, blank=True)
    skipped_reason = models.CharField(max_length=200, blank=True)

    archived_at = models.DateTimeField(null=True, blank=True)
    archived_reason = models.CharField(max_length=200, blank=True)

    @property
    def duration_days(self):
        """Calculates duration based on planned dates."""
        return (self.planned_end_date - self.planned_start_date).days

    @property
    def duration_weeks(self):
        """Calculates duration in weeks, rounding up."""
        return math.ceil(self.duration_days / 7)

    class Meta:
        """Metadata options for ProgramPhase."""

        ordering = ["sequence_order"]
        constraints = [
            models.UniqueConstraint(
                fields=["sequence_order", "program"],
                name="unique_sequence_order_per_program",
            )
        ]

    def clean(self):
        """Validates phase lifecycle and state-dependent timestamps.

        Raises:
            ValidationError: If sequence, dates, or status-specific
                requirements are not met.
        """
        super().clean()

        status_code = self.status.code

        if self.sequence_order <= 0:
            raise ValidationError("Phase sequence order must be greater than 0.")

        if self.planned_start_date >= self.planned_end_date:
            raise ValidationError("Planned start date must be before planned end date.")

        if self.actual_start_date and self.actual_end_date:
            if self.actual_start_date > self.actual_end_date:
                raise ValidationError(
                    "Actual start date cannot be after actual end date."
                )

        if self.started_at and not self.actual_start_date:
            raise ValidationError("Started phases must record an actual start date.")

        if self.completed_at and not self.actual_end_date:
            raise ValidationError("Completed phases must record an actual end date.")

        if status_code == ProgramPhaseStatusesVocabulary.ACTIVE:
            if not self.phase_goal:
                raise ValidationError("Active phases must clearly outline a goal.")
            if not self.actual_start_date:
                raise ValidationError("Active phases must record an actual start date.")
            if not self.started_at:
                raise ValidationError("Active phases must record when they started.")

        if status_code == ProgramPhaseStatusesVocabulary.COMPLETED:
            if not self.completed_at:
                raise ValidationError(
                    "Completed phases must record when they were completed."
                )
            if not self.actual_start_date or not self.actual_end_date:
                raise ValidationError(
                    "Completed phases must record actual start and end dates."
                )
            if not self.started_at:
                raise ValidationError("Completed phases must record when they started.")

        if status_code == ProgramPhaseStatusesVocabulary.SKIPPED:
            if not self.skipped_at:
                raise ValidationError(
                    "Skipped phases must record when they were skipped."
                )
            if not self.skipped_reason:
                raise ValidationError("Skipped phases must record a reason.")

        if status_code == ProgramPhaseStatusesVocabulary.ARCHIVED:
            if not self.archived_at:
                raise ValidationError(
                    "Archived phases must record when they were archived."
                )
            if not self.archived_reason:
                raise ValidationError("Archived phases must record a reason.")

        if (
            self.skipped_reason
            and status_code != ProgramPhaseStatusesVocabulary.SKIPPED
        ):
            raise ValidationError(
                "Skipped reason can only be tracked on skipped phases."
            )

        if (
            self.archived_reason
            and status_code != ProgramPhaseStatusesVocabulary.ARCHIVED
        ):
            raise ValidationError(
                "Archived reason can only be tracked on archived phases."
            )

        if (
            self.completed_at
            and status_code != ProgramPhaseStatusesVocabulary.COMPLETED
        ):
            raise ValidationError(
                "Only completed phases can record a completion timestamp."
            )

        if self.skipped_at and status_code != ProgramPhaseStatusesVocabulary.SKIPPED:
            raise ValidationError("Only skipped phases can record a skipped timestamp.")

        if self.archived_at and status_code != ProgramPhaseStatusesVocabulary.ARCHIVED:
            raise ValidationError(
                "Only archived phases can record an archived timestamp."
            )

        if self.completed_at and self.skipped_at:
            raise ValidationError("A phase cannot be both completed and skipped.")

        if self.completed_at and self.archived_at:
            raise ValidationError("A phase cannot be both completed and archived.")

        if self.skipped_at and self.archived_at:
            raise ValidationError("A phase cannot be both skipped and archived.")

        if self.created_by_trainer and not self.created_by_trainer.is_trainer:
            raise ValidationError("Program phases can only be created by trainers.")

    def save(self, *args, **kwargs):
        """Validates the model before saving."""
        self.full_clean()
        return super().save(*args, **kwargs)

    def __str__(self) -> str:
        return f"{self.phase_name or self.phase_option.label} of {self.program.program_name}"
