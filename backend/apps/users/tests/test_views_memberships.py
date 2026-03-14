import pytest
from django.contrib.auth import get_user_model
from django.utils import timezone
from model_bakery import baker
from rest_framework import status

from apps.users.models import (
    TrainerClientMembership,
)

User = get_user_model()
pytestmark = pytest.mark.django_db


@pytest.fixture
def membership_world(active_status, trainer_user_a, trainer_user_b, client_user):
    now = timezone.now()

    mem_a = baker.make(
        TrainerClientMembership,
        trainer=trainer_user_a.trainer_profile,
        client=baker.make(User, is_client=True).client_profile,
        status=active_status,
        responded_at=now,
        started_at=now,
    )

    mem_b = baker.make(
        TrainerClientMembership,
        trainer=trainer_user_b.trainer_profile,
        client=baker.make(User, is_client=True).client_profile,
        status=active_status,
        responded_at=now,
        started_at=now,
    )

    mem_client = baker.make(
        TrainerClientMembership,
        trainer=baker.make(User, is_trainer=True).trainer_profile,
        client=client_user.client_profile,
        status=active_status,
        responded_at=now,
        started_at=now,
    )

    return {
        "trainer_a": trainer_user_a,
        "trainer_b": trainer_user_b,
        "client": client_user,
        "mem_a": mem_a,
        "mem_b": mem_b,
        "mem_c": mem_client,
    }


def test_membership_list_isolated_for_trainers(
    trainer_a_membership_response, response_items
):
    response, membership_world = trainer_a_membership_response

    assert response.status_code == status.HTTP_200_OK

    items = response_items(response)
    returned_ids = [item["id"] for item in items]

    assert str(membership_world["mem_a"].id) in returned_ids
    assert str(membership_world["mem_b"].id) not in returned_ids
    assert str(membership_world["mem_c"].id) not in returned_ids


def test_membership_list_isolated_for_client(
    client_membership_response, response_items
):
    response, membership_world = client_membership_response

    assert response.status_code == status.HTTP_200_OK

    items = response_items(response)
    returned_ids = [item["id"] for item in items]

    assert str(membership_world["mem_c"].id) in returned_ids
    assert str(membership_world["mem_a"].id) not in returned_ids
    assert str(membership_world["mem_b"].id) not in returned_ids


def test_membership_list_requires_authentication(api_client):
    response = api_client.get("/api/v1/users/trainer-client-memberships/")
    assert response.status_code == status.HTTP_401_UNAUTHORIZED
