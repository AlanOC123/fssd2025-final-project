import pytest
from django.urls import reverse

pytestmark = pytest.mark.django_db


class TestWorkoutViewSet:

    def test_trainer_can_list_own_workouts(self, trainer_api_client, workout):
        url = reverse("workouts-list")
        response = trainer_api_client.get(url)

        assert response.status_code == 200
        ids = [item["id"] for item in response.data["results"]]
        assert str(workout.id) in ids

    def test_client_can_list_own_workouts(self, client_api_client, workout):
        url = reverse("workouts-list")
        response = client_api_client.get(url)

        assert response.status_code == 200
        ids = [item["id"] for item in response.data["results"]]
        assert str(workout.id) in ids

    def test_other_trainer_cannot_see_unrelated_workout(
        self, other_trainer_api_client, workout
    ):
        url = reverse("workouts-list")
        response = other_trainer_api_client.get(url)

        assert response.status_code == 200
        assert response.data["results"] == []

    def test_unauthenticated_request_is_rejected(self, api_client, workout):
        url = reverse("workouts-list")
        response = api_client.get(url)

        assert response.status_code == 401

    def test_trainer_can_create_workout(self, trainer_api_client, active_phase):
        url = reverse("workouts-list")
        payload = {
            "program_phase_id": str(active_phase.id),
            "workout_name": "Monday Lower",
            "planned_date": "2025-06-02",
        }
        response = trainer_api_client.post(url, payload, format="json")

        assert response.status_code == 201
        assert response.data["workout_name"] == "Monday Lower"

    def test_client_cannot_create_workout(self, client_api_client, active_phase):
        url = reverse("workouts-list")
        payload = {
            "program_phase_id": str(active_phase.id),
            "workout_name": "Sneaky Workout",
            "planned_date": "2025-06-02",
        }
        response = client_api_client.post(url, payload, format="json")

        assert response.status_code == 403

    def test_trainer_can_update_own_workout(self, trainer_api_client, workout):
        url = reverse("workouts-detail", args=[workout.id])
        payload = {
            "workout_name": "Updated Name",
            "program_phase_id": str(workout.program_phase.id),
        }
        response = trainer_api_client.patch(url, payload, format="json")

        assert response.status_code == 200
        assert response.data["workout_name"] == "Updated Name"

    def test_client_cannot_update_workout(self, client_api_client, workout):
        url = reverse("workouts-detail", args=[workout.id])
        response = client_api_client.patch(
            url, {"workout_name": "Hacked"}, format="json"
        )

        assert response.status_code == 403

    def test_trainer_can_delete_own_workout(self, trainer_api_client, workout):
        url = reverse("workouts-detail", args=[workout.id])
        response = trainer_api_client.delete(url)

        assert response.status_code == 204

    def test_client_cannot_delete_workout(self, client_api_client, workout):
        url = reverse("workouts-detail", args=[workout.id])
        response = client_api_client.delete(url)

        assert response.status_code == 403

    def test_detail_response_includes_exercises_and_sets(
        self, trainer_api_client, workout, workout_exercise, workout_set
    ):
        url = reverse("workouts-detail", args=[workout.id])
        response = trainer_api_client.get(url)

        assert response.status_code == 200
        assert len(response.data["exercises"]) == 1
        assert len(response.data["exercises"][0]["sets"]) == 1

    def test_list_response_does_not_include_exercises(
        self, trainer_api_client, workout, workout_exercise
    ):
        url = reverse("workouts-list")
        response = trainer_api_client.get(url)

        assert response.status_code == 200
        first = response.data["results"][0]
        assert "exercises" not in first


class TestWorkoutExerciseViewSet:

    def test_trainer_can_create_exercise(self, trainer_api_client, workout, exercise):
        url = reverse("workout-exercises-list")
        payload = {
            "workout_id": str(workout.id),
            "exercise_id": str(exercise.id),
            "order": 1,
            "sets_prescribed": 3,
        }
        response = trainer_api_client.post(url, payload, format="json")

        assert response.status_code == 201
        assert response.data["sets_prescribed"] == 3

    def test_client_cannot_create_exercise(self, client_api_client, workout, exercise):
        url = reverse("workout-exercises-list")
        payload = {
            "workout_id": str(workout.id),
            "exercise_id": str(exercise.id),
            "order": 1,
            "sets_prescribed": 3,
        }
        response = client_api_client.post(url, payload, format="json")

        assert response.status_code == 403

    def test_trainer_can_delete_exercise(self, trainer_api_client, workout_exercise):
        url = reverse("workout-exercises-detail", args=[workout_exercise.id])
        response = trainer_api_client.delete(url)

        assert response.status_code == 204

    def test_client_can_read_exercise_with_instructions(
        self, client_api_client, workout_exercise
    ):
        url = reverse("workout-exercises-detail", args=[workout_exercise.id])
        response = client_api_client.get(url)

        assert response.status_code == 200
        assert "instructions" in response.data["exercise"]
        assert "safety_tips" in response.data["exercise"]

    def test_duplicate_order_within_workout_is_rejected(
        self, trainer_api_client, workout, exercise, workout_exercise
    ):
        # workout_exercise already occupies order=1
        url = reverse("workout-exercises-list")
        payload = {
            "workout_id": str(workout.id),
            "exercise_id": str(exercise.id),
            "order": 1,
            "sets_prescribed": 2,
        }
        response = trainer_api_client.post(url, payload, format="json")

        assert response.status_code == 400


class TestWorkoutSetViewSet:

    def test_trainer_can_create_set(self, trainer_api_client, workout_exercise):
        url = reverse("workout-sets-list")
        payload = {
            "workout_exercise_id": str(workout_exercise.id),
            "set_order": 1,
            "reps_prescribed": 5,
            "weight_prescribed": "100.00",
        }
        response = trainer_api_client.post(url, payload, format="json")

        assert response.status_code == 201
        assert response.data["reps_prescribed"] == 5

    def test_client_cannot_create_set(self, client_api_client, workout_exercise):
        url = reverse("workout-sets-list")
        payload = {
            "workout_exercise_id": str(workout_exercise.id),
            "set_order": 1,
            "reps_prescribed": 5,
            "weight_prescribed": "100.00",
        }
        response = client_api_client.post(url, payload, format="json")

        assert response.status_code == 403

    def test_negative_weight_is_rejected(self, trainer_api_client, workout_exercise):
        url = reverse("workout-sets-list")
        payload = {
            "workout_exercise_id": str(workout_exercise.id),
            "set_order": 1,
            "reps_prescribed": 5,
            "weight_prescribed": "-10.00",
        }
        response = trainer_api_client.post(url, payload, format="json")

        assert response.status_code == 400

    def test_zero_reps_is_rejected(self, trainer_api_client, workout_exercise):
        url = reverse("workout-sets-list")
        payload = {
            "workout_exercise_id": str(workout_exercise.id),
            "set_order": 1,
            "reps_prescribed": 0,
            "weight_prescribed": "100.00",
        }
        response = trainer_api_client.post(url, payload, format="json")

        assert response.status_code == 400

    def test_trainer_can_delete_set(self, trainer_api_client, workout_set):
        url = reverse("workout-sets-detail", args=[workout_set.id])
        response = trainer_api_client.delete(url)

        assert response.status_code == 204
