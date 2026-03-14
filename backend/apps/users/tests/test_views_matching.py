import pytest
from django.contrib.auth import get_user_model
from model_bakery import baker
from rest_framework import status

User = get_user_model()
pytestmark = pytest.mark.django_db


@pytest.fixture
def matching_world(goal_strength, goal_muscle_mass, level_beginner, level_advanced):
    client_user = baker.make(User, is_client=True)
    client_profile = client_user.client_profile
    client_profile.goal = goal_strength
    client_profile.level = level_beginner
    client_profile.save()

    trainer_a = baker.make(
        User,
        is_trainer=True,
        first_name="Alice",
        last_name="Smith",
        email="alice.smith@apex.com",
    )

    trainer_a.trainer_profile.accepted_goals.add(goal_strength)
    trainer_a.trainer_profile.accepted_levels.add(level_beginner)

    trainer_b = baker.make(User, is_trainer=True)
    trainer_b.trainer_profile.accepted_goals.add(goal_muscle_mass)
    trainer_b.trainer_profile.accepted_levels.add(level_beginner)

    trainer_c = baker.make(User, is_trainer=True)
    trainer_c.trainer_profile.accepted_goals.add(goal_strength)
    trainer_c.trainer_profile.accepted_levels.add(level_advanced)

    return {
        "client_user": client_user,
        "trainer_a": trainer_a,
        "trainer_b": trainer_b,
        "trainer_c": trainer_c,
    }


@pytest.fixture
def trainer_a_matching_response(api_client, matching_world):

    api_client.force_authenticate(user=matching_world["trainer_a"])

    response = api_client.get("/api/v1/users/find-trainers/")

    return response, matching_world


@pytest.fixture
def client_matching_response(api_client, matching_world):

    api_client.force_authenticate(user=matching_world["client_user"])

    response = api_client.get("/api/v1/users/find-trainers/")

    return response, matching_world


def test_matching_returns_only_relevant_trainers(
    client_matching_response, response_items
):
    response, matching_world = client_matching_response

    assert response.status_code == status.HTTP_200_OK

    items = response_items(response)
    returned_ids = [item["id"] for item in items]

    assert str(matching_world["trainer_a"].trainer_profile.id) in returned_ids
    assert str(matching_world["trainer_b"].trainer_profile.id) not in returned_ids
    assert str(matching_world["trainer_c"].trainer_profile.id) not in returned_ids


def test_matching_serializer_fields(client_matching_response, response_items):
    response, _ = client_matching_response

    items = response_items(response)
    match = items[0]

    assert match["first_name"] == "Alice"
    assert match["last_name"] == "Smith"
    assert match["email"] == "alice.smith@apex.com"

    assert "label" in match["accepted_goals"][0]


def test_trainer_cannot_use_matches(trainer_a_matching_response, response_items):
    response, _ = trainer_a_matching_response

    assert response.status_code == status.HTTP_200_OK
    assert response_items(response) == []


def test_matching_requires_authentication(api_client):
    response = api_client.get("/api/v1/users/find-trainers/")
    assert response.status_code == status.HTTP_401_UNAUTHORIZED
