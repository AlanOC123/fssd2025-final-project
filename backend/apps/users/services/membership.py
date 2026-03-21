from django.core.exceptions import ValidationError
from django.utils import timezone

from apps.users.constants import MembershipVocabulary
from apps.users.models import MembershipStatus, TrainerClientMembership


class MembershipService:
    """Controls lifecycle of core membership logic"""

    @classmethod
    def _transition_map(cls):
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
        allowed = cls._transition_map().get(current_code, set())

        if target_code not in allowed:
            raise ValidationError(
                f"Invalid membership transition from '{current_code}' to '{target_code}'."
            )

    @staticmethod
    def _now():
        return timezone.now()

    @classmethod
    def _get_status(cls, code):
        return MembershipStatus.objects.get(code=code)

    @classmethod
    def _has_open_membership(cls, client_user, trainer_user):
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
        """Controls lifecycle of a requested membership"""

        print(trainer_user)

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
        """Controls lifecycle of an accepted membership"""
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
        """Controls lifecycle of a rejected membership"""

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
        """Controls lifecycle of a dissolved membership"""

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
        """Controls lifecycle of a renewed membership"""

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
