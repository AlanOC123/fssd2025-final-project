from django.core.exceptions import ValidationError
from django.utils import timezone

from apps.programs.constants import ProgramStatusesVocabulary
from apps.programs.models import Program, ProgramStatusOption

from .program_phases import ProgramPhaseService


class ProgramService:
    """Domain service for managing training program lifecycles.

    Handles business logic for program state transitions, ownership validation,
    and membership-dependent status updates.
    """

    @staticmethod
    def _now():
        """Returns the current timezone-aware datetime."""
        return timezone.now()

    @classmethod
    def _get_status(cls, code):
        """Retrieves a ProgramStatusOption instance by its code.

        Args:
            code: The string identifier for the status.

        Returns:
            The ProgramStatusOption instance.
        """
        return ProgramStatusOption.objects.get(code=code)

    @classmethod
    def _transition_map(cls):
        """Defines allowed state transitions for a Program.

        Returns:
            A dictionary mapping current status codes to sets of valid target codes.
        """
        return {
            ProgramStatusesVocabulary.CREATING: {
                ProgramStatusesVocabulary.REVIEW,
                ProgramStatusesVocabulary.ABANDONED,
            },
            ProgramStatusesVocabulary.REVIEW: {
                ProgramStatusesVocabulary.CREATING,
                ProgramStatusesVocabulary.READY,
                ProgramStatusesVocabulary.ABANDONED,
            },
            ProgramStatusesVocabulary.READY: {
                ProgramStatusesVocabulary.IN_PROGRESS,
                ProgramStatusesVocabulary.ABANDONED,
            },
            ProgramStatusesVocabulary.IN_PROGRESS: {
                ProgramStatusesVocabulary.COMPLETED,
                ProgramStatusesVocabulary.ABANDONED,
            },
            ProgramStatusesVocabulary.COMPLETED: set(),
            ProgramStatusesVocabulary.ABANDONED: set(),
        }

    @classmethod
    def _validate_transition(cls, current_code, target_code):
        """Validates if a status transition is permitted.

        Args:
            current_code: The current status code of the program.
            target_code: The status code intended for transition.

        Raises:
            ValidationError: If the transition is not allowed by the transition map.
        """
        allowed = cls._transition_map().get(current_code, set())

        if target_code not in allowed:
            raise ValidationError(
                f"Invalid program transition from {current_code} to {target_code}."
            )

    @classmethod
    def _validate_trainer(cls, trainer_user):
        """Validates that the user is a trainer with a valid profile.

        Args:
            trainer_user: The user object to validate.

        Returns:
            The validated user object.

        Raises:
            ValidationError: If the user is missing, not a trainer, or lacks a profile.
        """
        if not trainer_user:
            raise ValidationError("Trainer user not found.")

        if not trainer_user.is_trainer:
            raise ValidationError("Only a trainer can perform this action.")

        if not hasattr(trainer_user, "trainer_profile"):
            raise ValidationError("Invalid trainer user. Missing profile.")

        return trainer_user

    @classmethod
    def _validate_client(cls, client_user):
        """Validates that the user is a client with a valid profile.

        Args:
            client_user: The user object to validate.

        Returns:
            The validated user object.

        Raises:
            ValidationError: If the user is missing, not a client, or lacks a profile.
        """
        if not client_user:
            raise ValidationError("Client user not found.")

        if not client_user.is_client:
            raise ValidationError("Only a client can perform this action.")

        if not hasattr(client_user, "client_profile"):
            raise ValidationError("Invalid client user. Missing profile.")

        return client_user

    @classmethod
    def _validate_membership(cls, membership):
        """Validates that a membership exists and is active.

        Args:
            membership: The TrainerClientMembership instance.

        Returns:
            The validated membership instance.

        Raises:
            ValidationError: If membership is missing or inactive.
        """
        if not membership:
            raise ValidationError("Missing membership.")

        if not membership.is_active:
            raise ValidationError(
                "Trainer client membership must be active for this action."
            )

        return membership

    @classmethod
    def _validate_program(cls, program):
        """Validates existence of a program instance."""
        if not program:
            raise ValidationError("Missing program.")
        return program

    @classmethod
    def _validate_program_has_phases(cls, program):
        """Ensures a program has at least one phase before proceeding.

        Raises:
            ValidationError: If the program has no created phases.
        """
        if not program.has_created_phases:
            raise ValidationError("No phases have been created for this program yet.")

        return program

    @classmethod
    def _validate_trainer_owns_membership(cls, membership, trainer_user):
        """Validates that the trainer is the owner of the membership."""
        if membership.trainer != trainer_user.trainer_profile:
            raise ValidationError(
                "Only the trainer associated with the membership can perform this action."
            )

    @classmethod
    def _validate_client_owns_membership(cls, membership, client_user):
        """Validates that the client is the owner of the membership."""
        if membership.client != client_user.client_profile:
            raise ValidationError(
                "Only the client associated with the membership can perform this action."
            )

    @classmethod
    def _enforce_trainer_membership_access(cls, membership, trainer_user):
        """Full access validation for trainers over a specific membership."""
        membership = cls._validate_membership(membership)
        trainer_user = cls._validate_trainer(trainer_user)
        cls._validate_trainer_owns_membership(membership, trainer_user)
        return membership, trainer_user

    @classmethod
    def _enforce_client_membership_access(cls, membership, client_user):
        """Full access validation for clients over a specific membership."""
        membership = cls._validate_membership(membership)
        client_user = cls._validate_client(client_user)
        cls._validate_client_owns_membership(membership, client_user)
        return membership, client_user

    @classmethod
    def _inactive_membership_cleanup(cls, program):
        """Automatically abandons a program when its membership becomes inactive.

        Args:
            program: The Program instance to cleanup.

        Returns:
            The updated Program instance.
        """
        abandoned_code = ProgramStatusesVocabulary.ABANDONED
        abandoned_status = cls._get_status(abandoned_code)

        cls._validate_transition(program.status.code, abandoned_code)

        program.status = abandoned_status
        program.abandoned_at = cls._now()
        program.abandonment_reason = "Membership became inactive."

        ProgramPhaseService.archive_remaining_phases(
            program, "Membership became inactive."
        )

        program.save()
        return program

    @classmethod
    def _enforce_active_program_membership(cls, program):
        """Ensures the membership is active or performs cleanup.

        Raises:
            ValidationError: Explaining the program was archived due to inactive membership.
        """
        membership = program.trainer_client_membership

        try:
            cls._validate_membership(membership)
        except ValidationError as e:
            cls._inactive_membership_cleanup(program)
            raise ValidationError(
                "Membership became inactive. "
                "Program was archived. "
                "Reactivate the membership and create a new program to continue. "
                f"Cause: {e.message}"
            )

        return program, membership

    @classmethod
    def create(
        cls,
        *,
        trainer_user,
        trainer_client_membership,
        program_name,
        training_goal,
        experience_level,
    ):
        """Creates a new program in the 'CREATING' state.

        Args:
            trainer_user: The User instance creating the program.
            trainer_client_membership: The associated membership.
            program_name: Name of the program.
            training_goal: The TrainingGoal instance.
            experience_level: The ExperienceLevel instance.

        Returns:
            The newly created Program instance.
        """
        cls._enforce_trainer_membership_access(
            membership=trainer_client_membership,
            trainer_user=trainer_user,
        )

        status = cls._get_status(ProgramStatusesVocabulary.CREATING)

        program = Program.objects.create(
            program_name=program_name,
            trainer_client_membership=trainer_client_membership,
            training_goal=training_goal,
            experience_level=experience_level,
            created_by_trainer=trainer_user,
            last_edited_by=trainer_user,
            status=status,
        )

        return program

    @classmethod
    def submit_for_review(
        cls,
        *,
        program,
        submitting_user,
    ):
        """Submits a program to the client for review.

        Args:
            program: The Program instance.
            submitting_user: The trainer submitting the program.

        Returns:
            The updated Program instance.
        """
        program = cls._validate_program(program)
        program = cls._validate_program_has_phases(program)
        program, membership = cls._enforce_active_program_membership(program)

        cls._enforce_trainer_membership_access(membership, submitting_user)

        current_status_code = program.status.code
        next_status = cls._get_status(ProgramStatusesVocabulary.REVIEW)

        cls._validate_transition(
            current_code=current_status_code,
            target_code=next_status.code,
        )

        program.last_edited_by = submitting_user
        program.submitted_for_review_at = cls._now()
        program.status = next_status
        program.save()

        return program

    @classmethod
    def reviewed_by_client(
        cls,
        *,
        program,
        reviewed_by_user,
        feedback_notes,
        is_accepted,
    ):
        """Processes the outcome of a client review.

        Args:
            program: The Program instance.
            reviewed_by_user: The client user performing the review.
            feedback_notes: Optional feedback from the client.
            is_accepted: Boolean indicating if the program was approved.

        Returns:
            The updated Program instance.

        Raises:
            ValidationError: If rejection is submitted without feedback notes.
        """
        program = cls._validate_program(program)
        program = cls._validate_program_has_phases(program)
        program, membership = cls._enforce_active_program_membership(program)

        membership, reviewed_by_user = cls._enforce_client_membership_access(
            membership,
            reviewed_by_user,
        )

        current_status_code = program.status.code
        current_version = program.version

        next_status = (
            cls._get_status(ProgramStatusesVocabulary.READY)
            if is_accepted
            else cls._get_status(ProgramStatusesVocabulary.CREATING)
        )

        cls._validate_transition(current_status_code, next_status.code)

        if (
            next_status.code == ProgramStatusesVocabulary.CREATING
            and not feedback_notes
        ):
            raise ValidationError(
                "Please provide feedback notes when rejecting the program."
            )

        program.reviewed_at = cls._now()
        program.last_edited_by = reviewed_by_user
        program.review_notes = feedback_notes
        program.version = current_version + 1
        program.status = next_status
        program.save()

        return program

    @classmethod
    def start_program(
        cls,
        *,
        program,
        started_by_user,
    ):
        """Transitions a 'READY' program to 'IN_PROGRESS'.

        Args:
            program: The Program instance.
            started_by_user: The client user starting the program.

        Returns:
            The updated Program instance.
        """
        program = cls._validate_program(program)
        program = cls._validate_program_has_phases(program)
        program, membership = cls._enforce_active_program_membership(program)

        membership, started_by_user = cls._enforce_client_membership_access(
            membership,
            started_by_user,
        )

        current_status_code = program.status.code
        next_status = cls._get_status(ProgramStatusesVocabulary.IN_PROGRESS)

        cls._validate_transition(current_status_code, next_status.code)

        program.started_at = cls._now()
        program.status = next_status
        program.last_edited_by = started_by_user
        program.save()

        return program

    @classmethod
    def complete_program(
        cls,
        *,
        program,
        completed_by_user,
        completion_notes,
    ):
        """Marks a program as completed.

        Args:
            program: The Program instance.
            completed_by_user: The client user completing the program.
            completion_notes: Summary of progress made.

        Returns:
            The updated Program instance.

        Raises:
            ValidationError: If phases are unfinished or notes are missing.
        """
        program = cls._validate_program(program)
        program = cls._validate_program_has_phases(program)
        program, membership = cls._enforce_active_program_membership(program)

        if not program.all_phases_finished:
            raise ValidationError(
                "All program phases must be finished before the program can be completed."
            )

        if not completion_notes:
            raise ValidationError(
                "Please provide notes about the progress made during the program."
            )

        membership, completed_by_user = cls._enforce_client_membership_access(
            membership,
            completed_by_user,
        )

        current_status_code = program.status.code
        next_status = cls._get_status(ProgramStatusesVocabulary.COMPLETED)

        cls._validate_transition(current_status_code, next_status.code)

        program.completed_at = cls._now()
        program.completion_notes = completion_notes
        program.status = next_status
        program.last_edited_by = completed_by_user
        program.save()

        return program

    @classmethod
    def abandon_program(
        cls,
        *,
        program,
        abandoned_by_user,
        abandonment_reason,
    ):
        """Prematurely stops a program lifecycle.

        Args:
            program: The Program instance.
            abandoned_by_user: Either trainer or client owner.
            abandonment_reason: Explanation for stopping.

        Returns:
            The updated Program instance.

        Raises:
            ValidationError: If reason is missing or phases are not finished/archived.
        """
        program = cls._validate_program(program)

        if not abandonment_reason:
            raise ValidationError("Please provide a reason for abandoning the program.")

        membership = program.trainer_client_membership

        if abandoned_by_user.is_trainer:
            cls._enforce_trainer_membership_access(membership, abandoned_by_user)
        elif abandoned_by_user.is_client:
            cls._enforce_client_membership_access(membership, abandoned_by_user)
        else:
            raise ValidationError(
                "Only the trainer or client associated with the membership can abandon the program."
            )

        if not program.all_phases_finished:
            raise ValidationError(
                "All program phases must be finished before the program can be abandoned."
            )

        current_status_code = program.status.code
        next_status = cls._get_status(ProgramStatusesVocabulary.ABANDONED)

        cls._validate_transition(current_status_code, next_status.code)

        program.abandoned_at = cls._now()
        program.abandonment_reason = abandonment_reason
        program.status = next_status
        program.last_edited_by = abandoned_by_user
        program.save()

        return program
