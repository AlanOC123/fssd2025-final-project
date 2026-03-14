import pytest
from rest_framework import status

pytestmark = pytest.mark.django_db


@pytest.fixture
def exercise_api_world(
    dumbbell_equipment,
    barbell_equipment,
    beginner_level,
    advanced_level,
    dumbbell_bicep_curl_exercise,
    barbell_bench_press_exercise,
):
    return {
        "dumbbell_equipment": dumbbell_equipment,
        "barbell_equipment": barbell_equipment,
        "beginner_level": beginner_level,
        "advanced_level": advanced_level,
        "dumbbell_bicep_curl": dumbbell_bicep_curl_exercise,
        "barbell_bench_press": barbell_bench_press_exercise,
    }


def test_equipment_list_is_public(api_client, exercise_api_world, response_items):
    response = api_client.get("/api/v1/exercises/equipment/")
    status_code, _ = response_items(response)

    assert status_code == status.HTTP_200_OK


def test_equipment_list_returns_expected_contract(
    api_client, exercise_api_world, response_items
):
    response = api_client.get("/api/v1/exercises/equipment/")
    _, data = response_items(response)

    assert "id" in data[0]
    assert "label" in data[0]
    assert "equipment_name" not in data[0]
    assert "code" not in data[0]


def test_exercise_list_is_public(api_client, response_items):
    response = api_client.get("/api/v1/exercises/exercises/")
    status_code, _ = response_items(response)
    assert status_code == status.HTTP_200_OK


def test_exercise_list_returns_expected_contract(
    api_client, response_items, exercise_api_world
):
    response = api_client.get("/api/v1/exercises/exercises/")
    _, data = response_items(response)

    exercise = data[0]
    assert set(exercise.keys()) == {
        "id",
        "created_at",
        "updated_at",
        "exercise_name",
        "equipment",
        "experience_level",
        "instructions",
        "safety_tips",
    }


def test_exercise_list_excludes_internal_fields(
    api_client, response_items, exercise_api_world
):
    response = api_client.get("/api/v1/exercises/exercises/")
    _, data = response_items(response)

    exercise = data[0]
    assert set(exercise.keys()) != {"api_name", "is_enriched"}


def test_exercise_list_returns_compact_nested_contract(
    api_client, response_items, exercise_api_world
):
    response = api_client.get("/api/v1/exercises/exercises/")
    _, data = response_items(response)

    exercise = data[0]

    assert isinstance(exercise["equipment"], list)

    assertion_set = {"id", "label"}
    assert set(exercise["equipment"][0].keys()) == assertion_set
    assert set(exercise["experience_level"].keys()) == assertion_set
