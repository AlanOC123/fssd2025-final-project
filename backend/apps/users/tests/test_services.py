import pytest
from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from model_bakery import baker

from apps.users.models import MembershipStatus
from apps.users.services.membership import MembershipService

User = get_user_model()
pytestmark = pytest.mark.django_db

# test_services.py — replace the two local fixtures at the top


@pytest.fixture
def membership_setup():
    client_user = baker.make(User, is_client=True)
    trainer_user = baker.make(User, is_trainer=True)
    return client_user, trainer_user


def test_membership_request_flow(membership_setup):
    client, trainer = membership_setup

    membership = MembershipService.request(client_user=client, trainer_user=trainer)

    assert membership.status.code == "PENDING_TRAINER_REVIEW"
    assert membership.requested_at is not None


def test_membership_accept_flow(membership_setup):
    client, trainer = membership_setup

    membership = MembershipService.request(client_user=client, trainer_user=trainer)
    membership = MembershipService.accept(trainer_user=trainer, membership=membership)

    assert membership.status.code == "ACTIVE"
    assert membership.responded_at is not None
    assert membership.started_at is not None


def test_membership_reject_flow(membership_setup):
    client, trainer = membership_setup

    membership = MembershipService.request(client_user=client, trainer_user=trainer)
    membership = MembershipService.reject(trainer_user=trainer, membership=membership)

    assert membership.status.code == "REJECTED"
    assert membership.responded_at is not None
    assert membership.started_at is None


def test_client_membership_dissolution_flow(membership_setup):
    client, trainer = membership_setup

    membership = MembershipService.request(client_user=client, trainer_user=trainer)
    membership = MembershipService.accept(trainer_user=trainer, membership=membership)

    membership = MembershipService.dissolve(membership=membership, acting_user=client)

    assert membership.status.code == "DISSOLVED_BY_CLIENT"
    assert membership.ended_at is not None
    assert membership.ended_by == client


def test_trainer_membership_dissolution_flow(membership_setup):
    client, trainer = membership_setup

    membership = MembershipService.request(client_user=client, trainer_user=trainer)
    membership = MembershipService.accept(trainer_user=trainer, membership=membership)

    membership = MembershipService.dissolve(membership=membership, acting_user=trainer)

    assert membership.status.code == "DISSOLVED_BY_TRAINER"
    assert membership.ended_at is not None
    assert membership.ended_by == trainer


def test_membership_renewal_flow(membership_setup):
    client, trainer = membership_setup

    membership = MembershipService.request(client_user=client, trainer_user=trainer)
    membership = MembershipService.accept(trainer_user=trainer, membership=membership)

    membership = MembershipService.dissolve(membership=membership, acting_user=client)

    renewed = MembershipService.renew(client_user=client, trainer_user=trainer)

    assert renewed.previous_membership == membership
    assert renewed.status.code == "PENDING_TRAINER_REVIEW"


@pytest.mark.parametrize("action", [MembershipService.accept, MembershipService.reject])
def test_only_trainer_can_respond(membership_setup, action):
    client, trainer = membership_setup

    membership = MembershipService.request(client_user=client, trainer_user=trainer)

    with pytest.raises(ValidationError):
        action(membership=membership, trainer_user=client)


def test_cannot_accept_non_pending(membership_setup):
    client, trainer = membership_setup

    membership = MembershipService.request(client_user=client, trainer_user=trainer)
    membership = MembershipService.reject(membership=membership, trainer_user=trainer)

    with pytest.raises(ValidationError):
        MembershipService.accept(membership=membership, trainer_user=trainer)
