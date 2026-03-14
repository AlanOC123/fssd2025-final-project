import pytest

pytestmark = pytest.mark.django_db


@pytest.fixture
def exercise_filter_world(
    beginner_level,
    advanced_level,
    dumbbell_equipment,
    barbell_equipment,
    upper_arm_group,
    chest_group,
    biceps_muscle,
    pec_major_muscle,
    dumbbell_bicep_curl_exercise,
    barbell_bench_press_exercise,
    concentric_bicep_curl_movement,
    concentric_bench_press_movement,
    elbow_flexion_joint_contribution,
    horizontal_adduction_joint_contribution,
    bicep_elbow_flexion_involvement,
    pec_major_horizontal_adduction_involvement,
):
    return {
        "beginner_level": beginner_level,
        "advanced_level": advanced_level,
        "dumbbell_equipment": dumbbell_equipment,
        "barbell_equipment": barbell_equipment,
        "upper_arm_group": upper_arm_group,
        "chest_group": chest_group,
        "biceps_muscle": biceps_muscle,
        "pec_major_muscle": pec_major_muscle,
        "dumbbell_bicep_curl": dumbbell_bicep_curl_exercise,
        "barbell_bench_press": barbell_bench_press_exercise,
    }


def test_exercise_search_by_name(api_client, response_items, exercise_filter_world):
    response = api_client.get("/api/v1/exercises/exercises/?search=bicep+curl")
    _, data = response_items(response)

    assert (
        data[0]["exercise_name"]
        == exercise_filter_world["dumbbell_bicep_curl"].exercise_name
    )


def test_equipment_search_filters_results(
    api_client, response_items, exercise_filter_world
):
    response = api_client.get("/api/v1/exercises/equipment/?search=dumbb")
    _, data = response_items(response)

    response_labels = [item["label"] for item in data]
    assert exercise_filter_world["dumbbell_equipment"].label in response_labels
    assert exercise_filter_world["barbell_equipment"].label not in response_labels


@pytest.mark.parametrize(
    "query_param,value_getter,expected_key,excluded_key",
    [
        (
            "experience_level",
            lambda world: str(world["beginner_level"].id),
            "dumbbell_bicep_curl",
            "barbell_bench_press",
        ),
        (
            "equipment",
            lambda world: str(world["barbell_equipment"].id),
            "barbell_bench_press",
            "dumbbell_bicep_curl",
        ),
        (
            "target_muscle_id",
            lambda world: str(world["pec_major_muscle"].id),
            "barbell_bench_press",
            "dumbbell_bicep_curl",
        ),
        (
            "target_muscle_label",
            lambda world: "pec",
            "barbell_bench_press",
            "dumbbell_bicep_curl",
        ),
        (
            "target_muscle_group_id",
            lambda world: str(world["upper_arm_group"].id),
            "dumbbell_bicep_curl",
            "barbell_bench_press",
        ),
        (
            "target_muscle_group_label",
            lambda world: "upper arm",
            "dumbbell_bicep_curl",
            "barbell_bench_press",
        ),
    ],
    ids=[
        "filters by experience level",
        "filters by equipment",
        "filters by target muscle id",
        "filters by target muscle label",
        "filters by target muscle group id",
        "filters by target muscle group label",
    ],
)
def test_exercise_filters(
    api_client,
    response_items,
    exercise_filter_world,
    query_param,
    value_getter,
    expected_key,
    excluded_key,
):
    value = value_getter(exercise_filter_world)

    response = api_client.get(f"/api/v1/exercises/exercises/?{query_param}={value}")
    _, data = response_items(response)

    response_ids = [item["id"] for item in data]

    assert str(exercise_filter_world[expected_key].id) in response_ids
    assert str(exercise_filter_world[excluded_key].id) not in response_ids


def test_exercise_list_default_ordering_is_by_exercise_name(
    api_client, response_items, exercise_filter_world
):
    response = api_client.get("/api/v1/exercises/exercises/")
    _, data = response_items(response)

    names = [item["exercise_name"] for item in data]

    assert names == sorted(names)


@pytest.mark.parametrize(
    "query_string,reverse",
    [
        ("", False),
        ("?ordering=-exercise_name", True),
    ],
    ids=["default ascending ordering", "descending ordering"],
)
def test_exercise_ordering(
    api_client,
    response_items,
    exercise_filter_world,
    query_string,
    reverse,
):
    response = api_client.get(f"/api/v1/exercises/exercises/{query_string}")
    _, data = response_items(response)

    names = [item["exercise_name"] for item in data]
    assert names == sorted(names, reverse=reverse)
