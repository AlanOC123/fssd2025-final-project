from django.core.exceptions import ValidationError
from django.db import transaction
from django.utils import timezone

from apps.programs.constants import (
    ProgramPhaseStatusesVocabulary,
    ProgramStatusesVocabulary,
)
from apps.programs.models import ProgramPhase, ProgramPhaseStatusOption


class ProgramPhaseService:
    """Domain service for managing individual ProgramPhase lifecycles.

    Handles business logic for phase transitions, validation of state-dependent
    actions, and synchronization of the 'next' phase in the program queue.
    """

    @staticmethod
    def _now():
        """Returns the current timezone-aware datetime."""
        return timezone.now()

    @staticmethod
    def _today():
        """Returns the current local date."""
        return timezone.localdate()

    @classmethod
    def _get_status(cls, code):
        """Retrieves a ProgramPhaseStatusOption instance by its code.

        Args:
            code: The string identifier for the status.

        Returns:
            The ProgramPhaseStatusOption instance.

        Raises:
            ValidationError: If the status code does not exist in the database.
        """
        try:
            return ProgramPhaseStatusOption.objects.get(code=code)
        except ProgramPhaseStatusOption.DoesNotExist as exc:
            raise ValidationError(f"Unknown program phase status: {code}.") from exc

    @classmethod
    def _transition_map(cls):
        """Defines the allowed status transitions for a ProgramPhase.

        Returns:
            A dictionary mapping current status codes to sets of valid target codes.
        """
        return {
            ProgramPhaseStatusesVocabulary.PLANNED: {
                ProgramPhaseStatusesVocabulary.NEXT,
                ProgramPhaseStatusesVocabulary.SKIPPED,
                ProgramPhaseStatusesVocabulary.ARCHIVED,
            },
            ProgramPhaseStatusesVocabulary.NEXT: {
                ProgramPhaseStatusesVocabulary.PLANNED,
                ProgramPhaseStatusesVocabulary.ACTIVE,
                ProgramPhaseStatusesVocabulary.SKIPPED,
                ProgramPhaseStatusesVocabulary.ARCHIVED,
            },
            ProgramPhaseStatusesVocabulary.ACTIVE: {
                ProgramPhaseStatusesVocabulary.COMPLETED,
                ProgramPhaseStatusesVocabulary.ARCHIVED,
            },
            ProgramPhaseStatusesVocabulary.SKIPPED: {
                ProgramPhaseStatusesVocabulary.PLANNED,
                ProgramPhaseStatusesVocabulary.ARCHIVED,
            },
            ProgramPhaseStatusesVocabulary.COMPLETED: set(),
            ProgramPhaseStatusesVocabulary.ARCHIVED: set(),
        }

    @classmethod
    def _validate_transition(cls, current_code, target_code):
        """Validates if a phase status transition is permitted.

        Args:
            current_code: The current status code of the phase.
            target_code: The status code intended for transition.

        Raises:
            ValidationError: If the status is unknown or the transition is forbidden.
        """
        transition_map = cls._transition_map()

        if current_code not in transition_map:
            raise ValidationError(f"Unknown program phase status '{current_code}'.")

        allowed = transition_map[current_code]

        if target_code not in allowed:
            raise ValidationError(
                f"Invalid program phase transition from '{current_code}' to '{target_code}'."
            )

    @classmethod
    def _validate_program_allows_phase_mutation(cls, program):
        """Ensures the parent program is in a state that allows phase edits.

        Args:
            program: The parent Program instance.

        Raises:
            ValidationError: If the program is completed, abandoned, or otherwise
                locked for edits.
        """
        allowed_program_statuses = {
            ProgramStatusesVocabulary.CREATING,
            ProgramStatusesVocabulary.REVIEW,
            ProgramStatusesVocabulary.READY,
            ProgramStatusesVocabulary.IN_PROGRESS,
        }

        program_status_code = program.status.code

        if program_status_code not in allowed_program_statuses:
            raise ValidationError(
                f"Program phases cannot be modified while program is in "
                f"'{program_status_code}' status."
            )

    @classmethod
    def _validate_no_other_active_phase(cls, program, excluding_phase=None):
        """Enforces a single-active-phase constraint for a program.

        Args:
            program: The parent Program instance.
            excluding_phase: Optional phase to ignore (e.g., the current phase).

        Raises:
            ValidationError: If an active phase already exists for the program.
        """
        qs = ProgramPhase.objects.filter(
            program=program,
            status__code=ProgramPhaseStatusesVocabulary.ACTIVE,
        )

        if excluding_phase is not None:
            qs = qs.exclude(pk=excluding_phase.pk)

        if qs.exists():
            raise ValidationError("Only one active phase is allowed per program.")

    @classmethod
    def _validate_phase_belongs_to_program(cls, phase, program):
        """Verifies that a phase is associated with the expected program."""
        if phase.program_id != program.id:
            raise ValidationError(
                "Program phase does not belong to the provided program."
            )

    @classmethod
    def _validate_can_be_marked_next(cls, phase):
        """Checks if a phase satisfies requirements to be the 'next' in queue.

        Args:
            phase: The ProgramPhase instance to validate.

        Raises:
            ValidationError: If the phase is not planned, if earlier phases
                exist in the queue, or if another phase is already 'next'.
        """
        current_code = phase.status.code

        if current_code != ProgramPhaseStatusesVocabulary.PLANNED:
            raise ValidationError(
                f"Only planned phases can be marked as next. Got '{current_code}'."
            )

        # Ensure no earlier phases (by sequence order) are still in planning/queue
        earlier_queued_phase_exists = ProgramPhase.objects.filter(
            program_id=phase.program_id,
            sequence_order__lt=phase.sequence_order,
            status__code__in=[
                ProgramPhaseStatusesVocabulary.PLANNED,
                ProgramPhaseStatusesVocabulary.NEXT,
            ],
        ).exists()

        if earlier_queued_phase_exists:
            raise ValidationError(
                "Only the earliest planned phase by sequence order may be marked as next."
            )

        other_next_qs = ProgramPhase.objects.filter(
            program_id=phase.program_id,
            status__code=ProgramPhaseStatusesVocabulary.NEXT,
        ).exclude(pk=phase.pk)

        if other_next_qs.exists():
            raise ValidationError(
                "Another phase is already marked as next for this program."
            )

    @classmethod
    def _validate_can_be_activated(cls, phase):
        """Validates all conditions required to transition a phase to active.

        Checks program mutation rights, active phase counts, ordering constraints,
        and current phase/program status.

        Args:
            phase: The ProgramPhase instance to validate.

        Raises:
            ValidationError: If any activation precondition is not met.
        """
        cls._validate_program_allows_phase_mutation(phase.program)
        cls._validate_no_other_active_phase(phase.program, excluding_phase=phase)
        cls._validate_ordering_constraints_for_activation(phase)

        current_code = phase.status.code

        if current_code != ProgramPhaseStatusesVocabulary.NEXT:
            raise ValidationError(
                f"Only the next phase in the queue can be activated. Got '{current_code}'."
            )

        if phase.program.status.code != ProgramStatusesVocabulary.IN_PROGRESS:
            raise ValidationError(
                "Program must be in progress before a phase can be activated."
            )

    @classmethod
    def _validate_can_be_completed(cls, phase):
        """Ensures a phase is in a state where it can be marked as completed."""
        cls._validate_program_allows_phase_mutation(phase.program)

        if phase.status.code != ProgramPhaseStatusesVocabulary.ACTIVE:
            raise ValidationError("Only an active phase can be completed.")

    @classmethod
    def _validate_ordering_constraints_for_activation(cls, phase):
        """Ensures no earlier phases are still incomplete or unarchived.

        Args:
            phase: The phase intended for activation.

        Raises:
            ValidationError: If blocking earlier phases are found.
        """
        blocking_phase_exists = (
            ProgramPhase.objects.filter(
                program_id=phase.program_id,
                sequence_order__lt=phase.sequence_order,
                status__code__in=[
                    ProgramPhaseStatusesVocabulary.PLANNED,
                    ProgramPhaseStatusesVocabulary.NEXT,
                    ProgramPhaseStatusesVocabulary.ACTIVE,
                ],
            )
            .exclude(pk=phase.pk)
            .exists()
        )

        if blocking_phase_exists:
            raise ValidationError(
                "A phase cannot be activated while an earlier unfinished phase exists."
            )

    @classmethod
    def _validate_phase_archive_allowed(cls, program):
        """Determines if the program state permits archiving of phases."""
        allowed_program_statuses = {
            ProgramStatusesVocabulary.CREATING,
            ProgramStatusesVocabulary.REVIEW,
            ProgramStatusesVocabulary.READY,
            ProgramStatusesVocabulary.IN_PROGRESS,
            ProgramStatusesVocabulary.ABANDONED,
            ProgramStatusesVocabulary.COMPLETED,
        }

        program_status_code = program.status.code

        if program_status_code not in allowed_program_statuses:
            raise ValidationError(
                f"Program phases cannot be archived while program is in "
                f"'{program_status_code}' status."
            )

    @classmethod
    def _set_phase_status(cls, phase, target_code, save_fields=None):
        """Updates a phase status with internal transition validation.

        Args:
            phase: The ProgramPhase instance.
            target_code: The desired status code.
            save_fields: Optional list of additional fields to include in the save.

        Returns:
            The updated ProgramPhase instance.
        """
        current_code = phase.status.code
        cls._validate_transition(current_code, target_code)

        phase.status = cls._get_status(target_code)

        update_fields = ["status"]

        if save_fields is not None:
            if not isinstance(save_fields, (list, tuple, set)):
                raise ValidationError("save_fields must be a list, tuple, or set.")
            update_fields.extend(save_fields)

        phase.save(update_fields=update_fields)
        return phase

    @classmethod
    def _clear_next_phase(cls, program):
        """Resets any existing 'NEXT' phase for a program back to 'PLANNED'."""
        ProgramPhase.objects.filter(
            program_id=program.id,
            status__code=ProgramPhaseStatusesVocabulary.NEXT,
        ).update(status=cls._get_status(ProgramPhaseStatusesVocabulary.PLANNED))

    @classmethod
    def _sync_next_phase(cls, program):
        """Synchronizes the 'NEXT' status to the earliest planned phase.

        If an active phase exists, 'NEXT' is cleared. Otherwise, the earliest
        planned phase in sequence order is promoted to 'NEXT'.

        Args:
            program: The parent Program instance.

        Returns:
            The ProgramPhase promoted to 'NEXT', or None.
        """
        active_exists = ProgramPhase.objects.filter(
            program_id=program.id,
            status__code=ProgramPhaseStatusesVocabulary.ACTIVE,
        ).exists()

        if active_exists:
            cls._clear_next_phase(program)
            return None

        # Identify the earliest candidate for the next phase
        candidate = ProgramPhase.objects.filter(
            program_id=program.id,
            status__code__in=[
                ProgramPhaseStatusesVocabulary.PLANNED,
                ProgramPhaseStatusesVocabulary.NEXT,
            ],
        ).first()

        if candidate is None:
            return None

        existing_next = ProgramPhase.objects.filter(
            program_id=program.id,
            status__code=ProgramPhaseStatusesVocabulary.NEXT,
        ).first()

        # If current next is already the candidate, do nothing
        if existing_next and existing_next.pk == candidate.pk:
            return candidate

        cls._clear_next_phase(program)

        if candidate.status.code != ProgramPhaseStatusesVocabulary.NEXT:
            cls._validate_transition(
                candidate.status.code,
                ProgramPhaseStatusesVocabulary.NEXT,
            )
            candidate.status = cls._get_status(ProgramPhaseStatusesVocabulary.NEXT)
            candidate.save(update_fields=["status"])

        return candidate

    @classmethod
    @transaction.atomic
    def mark_as_next(cls, phase, edited_by=None):
        """Manually marks a planned phase as the next in queue.

        Args:
            phase: The ProgramPhase instance.
            edited_by: Optional User instance for audit tracking.

        Returns:
            The updated ProgramPhase instance.
        """
        cls._validate_program_allows_phase_mutation(phase.program)
        cls._validate_can_be_marked_next(phase)

        if phase.status.code != ProgramPhaseStatusesVocabulary.NEXT:
            phase.status = cls._get_status(ProgramPhaseStatusesVocabulary.NEXT)

            update_fields = ["status"]
            if edited_by is not None:
                phase.last_edited_by = edited_by
                update_fields.append("last_edited_by")

            phase.save(update_fields=update_fields)

        cls._sync_next_phase(phase.program)
        phase.refresh_from_db()
        return phase

    @classmethod
    @transaction.atomic
    def activate_phase(cls, phase, edited_by=None):
        """Transitions the next phase to the active state.

        Args:
            phase: The ProgramPhase instance to activate.
            edited_by: Optional User instance for audit tracking.

        Returns:
            The activated ProgramPhase instance.
        """
        cls._validate_can_be_activated(phase)

        update_fields = []

        cls._validate_transition(
            phase.status.code,
            ProgramPhaseStatusesVocabulary.ACTIVE,
        )
        phase.status = cls._get_status(ProgramPhaseStatusesVocabulary.ACTIVE)
        update_fields.append("status")

        if phase.actual_start_date is None:
            phase.actual_start_date = cls._today()
            update_fields.append("actual_start_date")

        if phase.started_at is None:
            phase.started_at = cls._now()
            update_fields.append("started_at")

        if edited_by is not None:
            phase.last_edited_by = edited_by
            update_fields.append("last_edited_by")

        phase.save(update_fields=update_fields)

        cls._sync_next_phase(phase.program)
        phase.refresh_from_db()
        return phase

    @classmethod
    @transaction.atomic
    def complete_phase(cls, phase, edited_by=None):
        """Transitions an active phase to the completed state.

        Args:
            phase: The ProgramPhase instance to complete.
            edited_by: Optional User instance for audit tracking.

        Returns:
            The completed ProgramPhase instance.
        """
        cls._validate_can_be_completed(phase)

        update_fields = []

        cls._validate_transition(
            phase.status.code,
            ProgramPhaseStatusesVocabulary.COMPLETED,
        )
        phase.status = cls._get_status(ProgramPhaseStatusesVocabulary.COMPLETED)
        update_fields.append("status")

        # Fallback for start dates if not previously recorded
        if phase.actual_start_date is None:
            phase.actual_start_date = cls._today()
            update_fields.append("actual_start_date")

        if phase.started_at is None:
            phase.started_at = cls._now()
            update_fields.append("started_at")

        # Record completion dates
        if phase.actual_end_date is None:
            phase.actual_end_date = cls._today()
            update_fields.append("actual_end_date")

        if phase.completed_at is None:
            phase.completed_at = cls._now()
            update_fields.append("completed_at")

        if edited_by is not None:
            phase.last_edited_by = edited_by
            update_fields.append("last_edited_by")

        phase.save(update_fields=update_fields)

        cls._sync_next_phase(phase.program)
        phase.refresh_from_db()
        return phase

    @classmethod
    @transaction.atomic
    def skip_phase(cls, phase, reason, edited_by=None):
        """Skips a planned or next phase with a mandatory reason.

        Args:
            phase: The ProgramPhase instance to skip.
            reason: Explanation for skipping the phase.
            edited_by: Optional User instance for audit tracking.

        Returns:
            The updated ProgramPhase instance.

        Raises:
            ValidationError: If the phase is not in a skippable state or reason is empty.
        """
        cls._validate_program_allows_phase_mutation(phase.program)

        current_code = phase.status.code
        if current_code not in {
            ProgramPhaseStatusesVocabulary.PLANNED,
            ProgramPhaseStatusesVocabulary.NEXT,
        }:
            raise ValidationError(
                f"Program phase in '{current_code}' status cannot be skipped."
            )

        if not reason or not reason.strip():
            raise ValidationError("Skipped phases must include a reason.")

        cls._validate_transition(current_code, ProgramPhaseStatusesVocabulary.SKIPPED)

        phase.status = cls._get_status(ProgramPhaseStatusesVocabulary.SKIPPED)
        phase.skipped_at = cls._now()
        phase.skipped_reason = reason.strip()

        update_fields = ["status", "skipped_at", "skipped_reason"]

        if edited_by is not None:
            phase.last_edited_by = edited_by
            update_fields.append("last_edited_by")

        phase.save(update_fields=update_fields)

        cls._sync_next_phase(phase.program)
        phase.refresh_from_db()
        return phase

    @classmethod
    @transaction.atomic
    def restore_to_planned(cls, phase, edited_by=None):
        """Restores a skipped or next phase back to the planned state.

        Args:
            phase: The ProgramPhase instance.
            edited_by: Optional User instance for audit tracking.

        Returns:
            The updated ProgramPhase instance.
        """
        cls._validate_program_allows_phase_mutation(phase.program)

        current_code = phase.status.code
        if current_code not in {
            ProgramPhaseStatusesVocabulary.SKIPPED,
            ProgramPhaseStatusesVocabulary.NEXT,
        }:
            raise ValidationError(
                f"Program phase in '{current_code}' status cannot be restored to planned."
            )

        cls._validate_transition(current_code, ProgramPhaseStatusesVocabulary.PLANNED)

        phase.status = cls._get_status(ProgramPhaseStatusesVocabulary.PLANNED)
        update_fields = ["status"]

        if current_code == ProgramPhaseStatusesVocabulary.SKIPPED:
            phase.skipped_at = None
            phase.skipped_reason = ""
            update_fields.extend(["skipped_at", "skipped_reason"])

        if edited_by is not None:
            phase.last_edited_by = edited_by
            update_fields.append("last_edited_by")

        phase.save(update_fields=update_fields)

        cls._sync_next_phase(phase.program)
        phase.refresh_from_db()
        return phase

    @classmethod
    @transaction.atomic
    def archive_remaining_phases(cls, program, reason, edited_by=None):
        """Archives all non-finished phases for a program.

        Args:
            program: The parent Program instance.
            reason: Mandatory reason for archiving.
            edited_by: Optional User instance for audit tracking.

        Returns:
            The count of phases that were archived.
        """
        cls._validate_phase_archive_allowed(program)

        if not reason or not reason.strip():
            raise ValidationError("Archived phases must include a reason.")

        live_phases = ProgramPhase.objects.filter(
            program_id=program.id,
            status__code__in=[
                ProgramPhaseStatusesVocabulary.PLANNED,
                ProgramPhaseStatusesVocabulary.NEXT,
                ProgramPhaseStatusesVocabulary.ACTIVE,
                ProgramPhaseStatusesVocabulary.SKIPPED,
            ],
        )
        live_phase_count = live_phases.count()

        archive_status = cls._get_status(ProgramPhaseStatusesVocabulary.ARCHIVED)
        archived_reason = reason.strip()
        archived_at = cls._now()

        for phase in live_phases:
            current_code = phase.status.code

            cls._validate_transition(
                current_code,
                ProgramPhaseStatusesVocabulary.ARCHIVED,
            )

            phase.status = archive_status
            phase.archived_at = archived_at
            phase.archived_reason = archived_reason

            update_fields = ["status", "archived_at", "archived_reason"]

            if current_code == ProgramPhaseStatusesVocabulary.SKIPPED:
                phase.skipped_at = None
                phase.skipped_reason = ""
                update_fields.extend(["skipped_at", "skipped_reason"])

            if edited_by is not None:
                phase.last_edited_by = edited_by
                update_fields.append("last_edited_by")

            phase.save(update_fields=update_fields)

        return live_phase_count
