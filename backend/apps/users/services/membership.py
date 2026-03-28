from django.core.exceptions import ValidationError
from django.utils import timezone

from apps.users.constants import MembershipVocabulary
from apps.users.models import MembershipStatus, TrainerClientMembership


class MembershipService:
    """Controls the lifecycle and business logic of trainer-client memberships.

    This service handles state transitions, validation of membership requests,
    and management of active or dissolved relationships between users.
    """

    @classmethod
    def _transition_map(cls):
        """Defines allowed state transitions for memberships.

        Returns:
            dict: A mapping of current states to sets of valid target states.
        """
        return {
            MembershipVocabulary.PENDING: {
                MembershipVocabulary.ACTIVE,
                MembershipVocabulary.REJECTED,
            },
            MembershipVocabulary.ACTIVE: {
                MembershipVocabulary.DISSOLVED_BY_CLIENT,
                MembershipVocabulary.DISSOLVED_BY_TRAINER,
            },
            MembershipVocabulary.REJECTED: set(),
            MembershipVocabulary.DISSOLVED_BY_CLIENT: set(),
            MembershipVocabulary.DISSOLVED_BY_TRAINER: set(),
        }

    @classmethod
    def _validate_transition(cls, current_code, target_code):
        """Validates if a state transition is permitted.

        Args:
            current_code: The current status code of the membership.
            target_code: The desired status code to transition to.

        Raises:
            ValidationError: If the transition is not allowed by the state map.
        """
        allowed = cls._transition_map().get(current_code, set())

        if target_code not in allowed:
            raise ValidationError(
                f"Invalid membership transition from '{current_code}' to '{target_code}'."
            )

    @staticmethod
    def _now():
        """Returns the current timezone-aware timestamp.

        Returns:
            datetime: The current time.
        """
        return timezone.now()

    @classmethod
    def _get_status(cls, code):
        """Retrieves a MembershipStatus instance by its code.

        Args:
            code: The string code of the status.

        Returns:
            MembershipStatus: The status instance.
        """
        return MembershipStatus.objects.get(code=code)

    @classmethod
    def _has_open_membership(cls, client_user, trainer_user):
        """Checks for existing pending or active memberships.

        Args:
            client_user: The user instance for the client.
            trainer_user: The user instance for the trainer.

        Returns:
            bool: True if an open membership exists, False otherwise.
        """
        return TrainerClientMembership.objects.filter(
            client=client_user.client_profile,
            trainer=trainer_user.trainer_profile,
            status__code__in=[
                MembershipVocabulary.PENDING,
                MembershipVocabulary.ACTIVE,
            ],
        ).exists()

    @classmethod
    def _get_dissolved_membership(cls, client_user, trainer_user):
        """Retrieves the most recent dissolved membership between two users.

        Args:
            client_user: The user instance for the client.
            trainer_user: The user instance for the trainer.

        Returns:
            TrainerClientMembership: The latest dissolved membership or None.
        """
        return (
            TrainerClientMembership.objects.filter(
                client=client_user.client_profile,
                trainer=trainer_user.trainer_profile,
                status__code__in=[
                    MembershipVocabulary.DISSOLVED_BY_CLIENT,
                    MembershipVocabulary.DISSOLVED_BY_TRAINER,
                ],
            )
            .order_by("-ended_at", "-updated_at")
            .first()
        )

    @classmethod
    def request(cls, client_user, trainer_user):
        """Initiates a new membership request from a client to a trainer.

        Args:
            client_user: The user instance initiating the request.
            trainer_user: The trainer being requested.

        Returns:
            TrainerClientMembership: The newly created membership instance.

        Raises:
            ValidationError: If user roles are incorrect, profiles are missing,
                an open membership already exists, or a renewal is required.
        """
        if not client_user.is_client:
            raise ValidationError("Membership client must belong to a client user.")

        if not trainer_user.is_trainer:
            raise ValidationError("Membership trainer must belong to a trainer user.")

        if not hasattr(client_user, "client_profile"):
            raise ValidationError("Client user does not have a client profile.")

        if not hasattr(trainer_user, "trainer_profile"):
            raise ValidationError("Trainer user does not have a trainer profile.")

        previous_membership = cls._get_dissolved_membership(
            client_user=client_user,
            trainer_user=trainer_user,
        )

        if cls._has_open_membership(client_user=client_user, trainer_user=trainer_user):
            raise ValidationError(
                "There is already an open membership between these two."
            )

        if previous_membership is not None:
            raise ValidationError(
                "A previous membership already existed between these two. Call renew() instead."
            )

        return TrainerClientMembership.objects.create(
            client=client_user.client_profile,
            trainer=trainer_user.trainer_profile,
            status=cls._get_status(MembershipVocabulary.PENDING),
            requested_at=cls._now(),
        )

    @classmethod
    def accept(cls, membership, trainer_user):
        """Transitions a pending membership to active status.

        Args:
            membership: The membership instance to accept.
            trainer_user: The user instance of the trainer performing the action.

        Returns:
            TrainerClientMembership: The updated membership instance.

        Raises:
            ValidationError: If the actor is not the assigned trainer or the
                state transition is invalid.
        """
        if trainer_user != membership.trainer.user:
            raise ValidationError(
                "Only the associated trainer can accept this membership."
            )

        cls._validate_transition(
            current_code=membership.status.code, target_code=MembershipVocabulary.ACTIVE
        )

        now = cls._now()

        membership.status = cls._get_status(MembershipVocabulary.ACTIVE)
        membership.responded_at = now
        membership.started_at = now
        membership.save()

        return membership

    @classmethod
    def reject(cls, membership, trainer_user):
        """Transitions a pending membership to rejected status.

        Args:
            membership: The membership instance to reject.
            trainer_user: The user instance of the trainer performing the action.

        Returns:
            TrainerClientMembership: The updated membership instance.

        Raises:
            ValidationError: If the actor is not the assigned trainer or the
                state transition is invalid.
        """
        if trainer_user != membership.trainer.user:
            raise ValidationError("Only the trainer can reject this membership.")

        cls._validate_transition(membership.status.code, MembershipVocabulary.REJECTED)
        now = cls._now()

        membership.status = cls._get_status(MembershipVocabulary.REJECTED)
        membership.responded_at = now
        membership.save()

        return membership

    @classmethod
    def dissolve(cls, membership, acting_user):
        """Ends an active membership by transitioning it to a dissolved state.

        Args:
            membership: The membership instance to dissolve.
            acting_user: The user instance (client or trainer) ending the agreement.

        Returns:
            TrainerClientMembership: The updated membership instance.

        Raises:
            ValidationError: If the actor is not a party to the membership or the
                state transition is invalid.
        """
        if acting_user not in (membership.client.user, membership.trainer.user):
            raise ValidationError(
                "Only the associated trainer or client can dissolve this membership."
            )

        target_code = (
            MembershipVocabulary.DISSOLVED_BY_CLIENT
            if acting_user == membership.client.user
            else MembershipVocabulary.DISSOLVED_BY_TRAINER
        )

        cls._validate_transition(membership.status.code, target_code)
        now = cls._now()

        membership.status = cls._get_status(target_code)
        membership.ended_at = now
        membership.ended_by = acting_user
        membership.save()

        return membership

    @classmethod
    def renew(cls, client_user, trainer_user):
        """Creates a new membership request based on a previous dissolved relationship.

        Args:
            client_user: The user instance initiating the renewal.
            trainer_user: The trainer being requested for renewal.

        Returns:
            TrainerClientMembership: The newly created renewal request.

        Raises:
            ValidationError: If user roles are incorrect, an open membership exists,
                or no previous dissolved membership is found.
        """
        if not client_user.is_client:
            raise ValidationError("Membership client must belong to a client user.")

        if not trainer_user.is_trainer:
            raise ValidationError("Membership trainer must belong to a trainer user.")

        if not hasattr(client_user, "client_profile"):
            raise ValidationError("Client user does not have a client profile.")

        if not hasattr(trainer_user, "trainer_profile"):
            raise ValidationError("Trainer user does not have a trainer profile.")

        if cls._has_open_membership(client_user=client_user, trainer_user=trainer_user):
            raise ValidationError(
                "An active or pending membership already exists for this trainer and client."
            )

        prev_mem = cls._get_dissolved_membership(
            client_user=client_user, trainer_user=trainer_user
        )

        if prev_mem is None:
            raise ValidationError(
                "No previous dissolved membership was found. Did you mean to call request() instead?"
            )

        now = cls._now()

        return TrainerClientMembership.objects.create(
            client=client_user.client_profile,
            trainer=trainer_user.trainer_profile,
            status=cls._get_status(MembershipVocabulary.PENDING),
            requested_at=now,
            previous_membership=prev_mem,
        )
