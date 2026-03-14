import uuid

import pytest
from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from django.utils import timezone
from model_bakery import baker

from apps.users.models import (
    TrainerClientMembership,
)

User = get_user_model()
pytestmark = pytest.mark.django_db


def test_create_standard_user(test_emails, test_password):
    user = User.objects.create_user(
        email=test_emails["base"],
        password=test_password,
        is_active=True,
    )

    assert user.email == test_emails["base"]
    assert user.check_password(test_password)
    assert user.is_active
    assert isinstance(user.id, uuid.UUID)


def test_create_super_user(test_emails, test_password):
    """
    Test superuser permissions
    """
    admin = User.objects.create_superuser(
        email=test_emails["base"],
        password=test_password,
        is_active=True,
    )

    assert admin.is_superuser is True
    assert admin.is_staff is True


def test_user_not_trainer_and_client():
    user = baker.make(User, is_client=True)

    # Try check if a setting is_client and is_trainer triggers the error
    with pytest.raises(ValidationError):
        user.is_trainer = True
        user.save()


@pytest.mark.parametrize("profile_type", ["client_profile", "trainer_profile"])
def test_profile_auto_creation(profile_type):
    """
    Signal should automatically create a profile profile
    """

    # Create the user as a trainer
    user = baker.make(
        User,
        is_trainer=profile_type == "trainer_profile",
        is_client=profile_type == "client_profile",
    )

    # Assert the signal works
    assert hasattr(user, profile_type)
    assert getattr(user, profile_type).user == user


def test_dissolved_membership_allows_new_membership(
    client_user, trainer_user_a, trainer_user_b, active_status, dissolved_status
):
    now = timezone.now()

    old_mem = baker.make(
        TrainerClientMembership,
        client=client_user.client_profile,
        trainer=trainer_user_a.trainer_profile,
        status=dissolved_status,
        ended_at=now,
        ended_by=client_user,
    )

    new_mem = baker.make(
        TrainerClientMembership,
        client=client_user.client_profile,
        trainer=trainer_user_b.trainer_profile,
        status=active_status,
        responded_at=now,
        started_at=now,
    )

    assert new_mem.id is not None
    assert old_mem.id is not None


def test_cannot_have_two_active_memberships(client_user, trainer_user_a, active_status):
    now = timezone.now()

    baker.make(
        TrainerClientMembership,
        client=client_user.client_profile,
        trainer=trainer_user_a.trainer_profile,
        status=active_status,
        responded_at=now,
        started_at=now,
    )

    with pytest.raises(Exception):
        baker.make(
            TrainerClientMembership,
            client=client_user.client_profile,
            trainer=trainer_user_a.trainer_profile,
            status=active_status,
            responded_at=now,
            started_at=now,
        )
