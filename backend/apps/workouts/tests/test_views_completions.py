import pytest
from django.urls import reverse
from django.utils import timezone

from factories import (
    WorkoutCompletionRecordFactory,
    WorkoutExerciseCompletionRecordFactory,
    WorkoutExerciseFactory,
    WorkoutFactory,
    WorkoutSetCompletionRecordFactory,
    WorkoutSetFactory,
)

pytestmark = pytest.mark.django_db


class TestWorkoutSessionViewSet:

    def test_client_can_start_workout(self, client_api_client, workout):
        url = reverse("workout-sessions-start")
        response = client_api_client.post(
            url, {"workout_id": str(workout.id)}, format="json"
        )

        assert response.status_code == 201
        assert response.data["is_skipped"] is False
        assert response.data["completed_at"] is None

    def test_client_can_skip_workout(self, client_api_client, workout):
        url = reverse("workout-sessions-skip")
        response = client_api_client.post(
            url, {"workout_id": str(workout.id)}, format="json"
        )

        assert response.status_code == 201
        assert response.data["is_skipped"] is True

    def test_cannot_start_same_workout_twice(
        self, client_api_client, workout, client_user
    ):
        WorkoutCompletionRecordFactory(workout=workout, client=client_user)

        url = reverse("workout-sessions-start")
        response = client_api_client.post(
            url, {"workout_id": str(workout.id)}, format="json"
        )

        assert response.status_code == 400

    def test_trainer_cannot_start_workout(self, trainer_api_client, workout):
        url = reverse("workout-sessions-start")
        response = trainer_api_client.post(
            url, {"workout_id": str(workout.id)}, format="json"
        )

        assert response.status_code == 400

    def test_client_cannot_start_workout_on_inactive_phase(
        self, client_api_client, completed_phase
    ):

        workout = WorkoutFactory(program_phase=completed_phase)

        url = reverse("workout-sessions-start")
        response = client_api_client.post(
            url, {"workout_id": str(workout.id)}, format="json"
        )

        assert response.status_code == 400

    def test_client_can_finish_open_session(
        self, client_api_client, workout, client_user
    ):
        session = WorkoutCompletionRecordFactory(workout=workout, client=client_user)

        url = reverse("workout-sessions-finish", args=[session.id])
        response = client_api_client.post(url, {}, format="json")

        assert response.status_code == 200
        assert response.data["completed_at"] is not None

    def test_cannot_finish_already_completed_session(
        self, client_api_client, workout, client_user
    ):
        now = timezone.now()
        session = WorkoutCompletionRecordFactory(
            workout=workout,
            client=client_user,
            started_at=now,
            completed_at=now,
        )

        url = reverse("workout-sessions-finish", args=[session.id])
        response = client_api_client.post(url, {}, format="json")

        assert response.status_code == 400

    def test_cannot_finish_skipped_session(
        self, client_api_client, workout, client_user
    ):
        session = WorkoutCompletionRecordFactory(
            workout=workout,
            client=client_user,
            is_skipped=True,
            completed_at=None,
        )

        url = reverse("workout-sessions-finish", args=[session.id])
        response = client_api_client.post(url, {}, format="json")

        assert response.status_code == 400

    def test_trainer_can_read_client_sessions(
        self, trainer_api_client, workout, client_user
    ):
        WorkoutCompletionRecordFactory(workout=workout, client=client_user)

        url = reverse("workout-sessions-list")
        response = trainer_api_client.get(url)

        assert response.status_code == 200
        assert len(response.data["results"]) == 1

    def test_response_includes_duration_s(
        self, client_api_client, workout, client_user
    ):
        now = timezone.now()
        session = WorkoutCompletionRecordFactory(
            workout=workout,
            client=client_user,
            started_at=now - timezone.timedelta(seconds=1800),
            completed_at=now,
        )

        url = reverse("workout-sessions-detail", args=[session.id])
        response = client_api_client.get(url)

        assert response.status_code == 200
        assert response.data["duration_s"] == 1800


class TestWorkoutExerciseRecordViewSet:

    def test_client_can_start_exercise(
        self, client_api_client, workout_exercise, workout, client_user
    ):
        session = WorkoutCompletionRecordFactory(workout=workout, client=client_user)

        url = reverse("exercise-records-start")
        payload = {
            "workout_exercise_id": str(workout_exercise.id),
            "session_id": str(session.id),
        }
        response = client_api_client.post(url, payload, format="json")

        assert response.status_code == 201
        assert response.data["is_skipped"] is False

    def test_client_can_skip_exercise(
        self, client_api_client, workout_exercise, workout, client_user
    ):
        session = WorkoutCompletionRecordFactory(workout=workout, client=client_user)

        url = reverse("exercise-records-skip")
        payload = {
            "workout_exercise_id": str(workout_exercise.id),
            "session_id": str(session.id),
        }
        response = client_api_client.post(url, payload, format="json")

        assert response.status_code == 201
        assert response.data["is_skipped"] is True

    def test_cannot_start_exercise_on_skipped_session(
        self, client_api_client, workout_exercise, workout, client_user
    ):
        session = WorkoutCompletionRecordFactory(
            workout=workout, client=client_user, is_skipped=True, completed_at=None
        )

        url = reverse("exercise-records-start")
        payload = {
            "workout_exercise_id": str(workout_exercise.id),
            "session_id": str(session.id),
        }
        response = client_api_client.post(url, payload, format="json")

        assert response.status_code == 400

    def test_cannot_start_exercise_twice(
        self, client_api_client, workout_exercise, workout, client_user
    ):
        session = WorkoutCompletionRecordFactory(workout=workout, client=client_user)
        WorkoutExerciseCompletionRecordFactory(
            workout_completion_record=session,
            workout_exercise=workout_exercise,
        )

        url = reverse("exercise-records-start")
        payload = {
            "workout_exercise_id": str(workout_exercise.id),
            "session_id": str(session.id),
        }
        response = client_api_client.post(url, payload, format="json")

        assert response.status_code == 400

    def test_exercise_not_belonging_to_session_is_rejected(
        self, client_api_client, workout, workout_exercise, client_user, active_phase
    ):
        # Create a second unrelated workout in the same phase
        other_workout = WorkoutFactory(program_phase=active_phase)
        session = WorkoutCompletionRecordFactory(
            workout=other_workout, client=client_user
        )

        url = reverse("exercise-records-start")
        payload = {
            # workout_exercise belongs to `workout`, not `other_workout`
            "workout_exercise_id": str(workout_exercise.id),
            "session_id": str(session.id),
        }
        response = client_api_client.post(url, payload, format="json")

        assert response.status_code == 400

    def test_trainer_cannot_start_exercise(
        self, trainer_api_client, workout_exercise, workout, client_user
    ):
        session = WorkoutCompletionRecordFactory(workout=workout, client=client_user)

        url = reverse("exercise-records-start")
        payload = {
            "workout_exercise_id": str(workout_exercise.id),
            "session_id": str(session.id),
        }
        response = trainer_api_client.post(url, payload, format="json")

        assert response.status_code == 400


class TestWorkoutSetRecordViewSet:

    def test_client_can_complete_set(
        self, client_api_client, workout_set, workout_exercise, workout, client_user
    ):
        session = WorkoutCompletionRecordFactory(workout=workout, client=client_user)
        exercise_record = WorkoutExerciseCompletionRecordFactory(
            workout_completion_record=session,
            workout_exercise=workout_exercise,
        )

        url = reverse("set-records-complete")
        payload = {
            "workout_set_id": str(workout_set.id),
            "exercise_record_id": str(exercise_record.id),
            "reps_completed": 5,
            "weight_completed": "100.00",
            "difficulty_rating": 7,
        }
        response = client_api_client.post(url, payload, format="json")

        assert response.status_code == 201
        assert response.data["reps_completed"] == 5
        assert response.data["reps_diff"] == 0
        assert response.data["weight_diff"] == "0.00"

    def test_client_can_skip_set(
        self, client_api_client, workout_set, workout_exercise, workout, client_user
    ):
        session = WorkoutCompletionRecordFactory(workout=workout, client=client_user)
        exercise_record = WorkoutExerciseCompletionRecordFactory(
            workout_completion_record=session,
            workout_exercise=workout_exercise,
        )

        url = reverse("set-records-skip")
        payload = {
            "workout_set_id": str(workout_set.id),
            "exercise_record_id": str(exercise_record.id),
        }
        response = client_api_client.post(url, payload, format="json")

        assert response.status_code == 201
        assert response.data["is_skipped"] is True
        assert response.data["reps_diff"] is None

    def test_cannot_complete_set_twice(
        self, client_api_client, workout_set, workout_exercise, workout, client_user
    ):
        session = WorkoutCompletionRecordFactory(workout=workout, client=client_user)
        exercise_record = WorkoutExerciseCompletionRecordFactory(
            workout_completion_record=session,
            workout_exercise=workout_exercise,
        )
        WorkoutSetCompletionRecordFactory(
            exercise_completion_record=exercise_record,
            workout_set=workout_set,
        )

        url = reverse("set-records-complete")
        payload = {
            "workout_set_id": str(workout_set.id),
            "exercise_record_id": str(exercise_record.id),
            "reps_completed": 5,
            "weight_completed": "100.00",
        }
        response = client_api_client.post(url, payload, format="json")

        assert response.status_code == 400

    def test_cannot_complete_set_on_skipped_exercise(
        self, client_api_client, workout_set, workout_exercise, workout, client_user
    ):
        now = timezone.now()
        session = WorkoutCompletionRecordFactory(workout=workout, client=client_user)
        exercise_record = WorkoutExerciseCompletionRecordFactory(
            workout_completion_record=session,
            workout_exercise=workout_exercise,
            is_skipped=True,
            started_at=now,
            completed_at=now,
        )

        url = reverse("set-records-complete")
        payload = {
            "workout_set_id": str(workout_set.id),
            "exercise_record_id": str(exercise_record.id),
            "reps_completed": 5,
            "weight_completed": "100.00",
        }
        response = client_api_client.post(url, payload, format="json")

        assert response.status_code == 400

    def test_set_not_belonging_to_exercise_is_rejected(
        self,
        client_api_client,
        workout_exercise,
        workout,
        client_user,
        exercise,
        active_phase,
    ):
        # Create a second exercise and use its set against the first exercise record

        other_exercise = WorkoutExerciseFactory(
            workout=workout, exercise=exercise, order=2, sets_prescribed=1
        )
        other_set = WorkoutSetFactory(workout_exercise=other_exercise, set_order=1)

        session = WorkoutCompletionRecordFactory(workout=workout, client=client_user)
        exercise_record = WorkoutExerciseCompletionRecordFactory(
            workout_completion_record=session,
            workout_exercise=workout_exercise,
        )

        url = reverse("set-records-complete")
        payload = {
            "workout_set_id": str(other_set.id),
            "exercise_record_id": str(exercise_record.id),
            "reps_completed": 5,
            "weight_completed": "100.00",
        }
        response = client_api_client.post(url, payload, format="json")

        assert response.status_code == 400

    def test_reps_completed_zero_is_rejected(
        self, client_api_client, workout_set, workout_exercise, workout, client_user
    ):
        session = WorkoutCompletionRecordFactory(workout=workout, client=client_user)
        exercise_record = WorkoutExerciseCompletionRecordFactory(
            workout_completion_record=session,
            workout_exercise=workout_exercise,
        )

        url = reverse("set-records-complete")
        payload = {
            "workout_set_id": str(workout_set.id),
            "exercise_record_id": str(exercise_record.id),
            "reps_completed": 0,
            "weight_completed": "100.00",
        }
        response = client_api_client.post(url, payload, format="json")

        assert response.status_code == 400

    def test_difficulty_rating_out_of_range_is_rejected(
        self, client_api_client, workout_set, workout_exercise, workout, client_user
    ):
        session = WorkoutCompletionRecordFactory(workout=workout, client=client_user)
        exercise_record = WorkoutExerciseCompletionRecordFactory(
            workout_completion_record=session,
            workout_exercise=workout_exercise,
        )

        url = reverse("set-records-complete")
        payload = {
            "workout_set_id": str(workout_set.id),
            "exercise_record_id": str(exercise_record.id),
            "reps_completed": 5,
            "weight_completed": "100.00",
            "difficulty_rating": 11,
        }
        response = client_api_client.post(url, payload, format="json")

        assert response.status_code == 400

    def test_positive_reps_diff_is_correct(
        self, client_api_client, workout_set, workout_exercise, workout, client_user
    ):
        # workout_set has reps_prescribed=5, weight_prescribed=100.00
        session = WorkoutCompletionRecordFactory(workout=workout, client=client_user)
        exercise_record = WorkoutExerciseCompletionRecordFactory(
            workout_completion_record=session,
            workout_exercise=workout_exercise,
        )

        url = reverse("set-records-complete")
        payload = {
            "workout_set_id": str(workout_set.id),
            "exercise_record_id": str(exercise_record.id),
            "reps_completed": 8,
            "weight_completed": "95.00",
        }
        response = client_api_client.post(url, payload, format="json")

        assert response.status_code == 201
        assert response.data["reps_diff"] == 3
        assert response.data["weight_diff"] == "-5.00"
