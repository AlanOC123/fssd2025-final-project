import pytest
from model_bakery import baker
from rest_framework import status

from apps.biology.constants import MuscleGroupVocabulary
from apps.biology.models import Muscle, MuscleGroup

pytestmark = pytest.mark.django_db


@pytest.fixture
def biology_world():
    # Use unique codes so get_or_create in other fixtures can't collide
    groups = [
        MuscleGroup.objects.get_or_create(
            code=f"GROUP_{i}", defaults={"label": f"Group {i}"}
        )[0]
        for i in range(3)
    ]
    muscles = [
        Muscle.objects.get_or_create(
            code=f"MUSCLE_{i}", defaults={"label": f"Muscle {i}"}
        )[0]
        for i in range(3)
    ]
    return {"muscle": muscles, "muscle_group": groups}


@pytest.mark.parametrize("public_route", ["muscles", "muscle-groups"])
def test_public_biology_routes_exist(
    public_route, biology_world, get_response, response_items
):
    status_code, data = response_items(get_response(public_route))
    assert status_code == status.HTTP_200_OK
    assert len(data) >= 3


def test_muscles_returns_expected_fields(get_response, response_items):
    group, _ = MuscleGroup.objects.get_or_create(
        code=MuscleGroupVocabulary.CHEST,
        defaults={"label": "Chest"},
    )
    muscle, _ = Muscle.objects.get_or_create(
        code="PECTORALIS_MAJOR",
        defaults={"label": "Pectoralis Major", "muscle_group": group},
    )

    status_code, data = response_items(get_response("muscles"))

    assert status_code == status.HTTP_200_OK

    item = next((m for m in data if m["code"] == "PECTORALIS_MAJOR"), None)
    assert item is not None
    assert item["id"] == str(muscle.id)
    assert item["label"] == "Pectoralis Major"
    assert item["muscle_group"]["code"] == "CHEST"
    assert item["muscle_group"]["label"] == "Chest"
    assert item["anatomical_direction_id"] is None
    assert item["anatomical_direction_label"] is None


def test_muscles_search_filters_results(api_client):
    Muscle.objects.get_or_create(code="BICEPS_SEARCH", defaults={"label": "Biceps"})
    Muscle.objects.get_or_create(code="TRICEPS_SEARCH", defaults={"label": "Triceps"})

    response = api_client.get("/api/v1/biology/muscles/?search=Biceps")

    assert response.status_code == status.HTTP_200_OK
    data = response.data["results"] if "results" in response.data else response.data
    codes = [m["code"] for m in data]
    assert "BICEPS_SEARCH" in codes
    assert "TRICEPS_SEARCH" not in codes


def test_muscles_are_ordered_by_label(get_response, response_items):
    Muscle.objects.get_or_create(
        code="ORDER_TRICEPS", defaults={"label": "Triceps Order"}
    )
    Muscle.objects.get_or_create(
        code="ORDER_BICEPS", defaults={"label": "Biceps Order"}
    )

    status_code, data = response_items(get_response("muscles"))

    assert status_code == status.HTTP_200_OK
    labels = [item["label"] for item in data]
    assert labels == sorted(labels)
