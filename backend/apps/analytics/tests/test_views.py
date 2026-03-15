# apps/analytics/tests/test_views.py
"""
Tests for the analytics API views.
Uses the full workout + session fixture chain.
"""

from decimal import Decimal

import pytest
from django.urls import reverse
from django.utils import timezone

from apps.analytics.models import ExerciseSessionSnapshot
from factories import (
    WorkoutCompletionRecordFactory,
    WorkoutExerciseCompletionRecordFactory,
    WorkoutSetCompletionRecordFactory,
)

pytestmark = pytest.mark.django_db


@pytest.fixture
def completed_session(workout, workout_exercise, workout_set, client_user):
    """A fully completed session with one exercise and one set."""
    now = timezone.now()
    session = WorkoutCompletionRecordFactory(
        workout=workout,
        client=client_user,
        started_at=now - timezone.timedelta(seconds=3600),
        completed_at=now,
    )
    exercise_record = WorkoutExerciseCompletionRecordFactory(
        workout_completion_record=session,
        workout_exercise=workout_exercise,
    )
    WorkoutSetCompletionRecordFactory(
        exercise_completion_record=exercise_record,
        workout_set=workout_set,
        reps_completed=10,
        weight_completed=Decimal("60"),
    )
    return session


@pytest.fixture
def snapshot(completed_session, active_phase, workout_exercise):
    """Pre-computed snapshot for the completed session."""
    from apps.analytics.services.snapshot import compute_and_save_snapshot

    return compute_and_save_snapshot(
        program=active_phase.program,
        exercise=workout_exercise.exercise,
        session=completed_session,
    )


class TestExerciseLoadHistoryView:

    def test_trainer_can_access_load_history(
        self,
        trainer_api_client,
        active_phase,
        workout_exercise,
        snapshot,
    ):
        url = reverse(
            "exercise-load-history",
            kwargs={
                "program_id": active_phase.program.id,
                "exercise_id": workout_exercise.exercise.id,
            },
        )
        response = trainer_api_client.get(url)
        assert response.status_code == 200

    def test_returns_chronological_session_list(
        self,
        trainer_api_client,
        active_phase,
        workout_exercise,
        snapshot,
    ):
        url = reverse(
            "exercise-load-history",
            kwargs={
                "program_id": active_phase.program.id,
                "exercise_id": workout_exercise.exercise.id,
            },
        )
        response = trainer_api_client.get(url)
        assert len(response.data) == 1
        entry = response.data[0]
        assert "session_load" in entry
        assert "one_rep_max" in entry
        assert "completed_at" in entry
        assert "muscle_breakdown" in entry

    def test_client_cannot_access_load_history(
        self,
        client_api_client,
        active_phase,
        workout_exercise,
        snapshot,
    ):
        url = reverse(
            "exercise-load-history",
            kwargs={
                "program_id": active_phase.program.id,
                "exercise_id": workout_exercise.exercise.id,
            },
        )
        response = client_api_client.get(url)
        assert response.status_code == 403

    def test_unauthenticated_request_is_rejected(
        self,
        api_client,
        active_phase,
        workout_exercise,
    ):
        url = reverse(
            "exercise-load-history",
            kwargs={
                "program_id": active_phase.program.id,
                "exercise_id": workout_exercise.exercise.id,
            },
        )
        response = api_client.get(url)
        assert response.status_code == 401

    def test_no_data_returns_204(
        self,
        trainer_api_client,
        active_phase,
        workout_exercise,
    ):
        # No snapshot created — exercise exists but no sessions
        url = reverse(
            "exercise-load-history",
            kwargs={
                "program_id": active_phase.program.id,
                "exercise_id": workout_exercise.exercise.id,
            },
        )
        response = trainer_api_client.get(url)
        assert response.status_code == 204

    def test_other_trainer_cannot_access(
        self,
        other_trainer_api_client,
        active_phase,
        workout_exercise,
        snapshot,
    ):
        url = reverse(
            "exercise-load-history",
            kwargs={
                "program_id": active_phase.program.id,
                "exercise_id": workout_exercise.exercise.id,
            },
        )
        response = other_trainer_api_client.get(url)
        assert response.status_code == 403

    def test_muscle_group_filter_limits_breakdown(
        self,
        trainer_api_client,
        active_phase,
        workout_exercise,
        snapshot,
        bicep_elbow_flexion_involvement,
        elbow_flexion_joint_contribution,
    ):
        url = reverse(
            "exercise-load-history",
            kwargs={
                "program_id": active_phase.program.id,
                "exercise_id": workout_exercise.exercise.id,
            },
        )
        response = trainer_api_client.get(url, {"muscle_group": "Nonexistent"})
        assert response.status_code == 200
        entry = response.data[0]
        assert entry["muscle_breakdown"] == []

    def test_role_filter_limits_breakdown(
        self,
        trainer_api_client,
        active_phase,
        workout_exercise,
        snapshot,
        bicep_elbow_flexion_involvement,
        elbow_flexion_joint_contribution,
    ):
        url = reverse(
            "exercise-load-history",
            kwargs={
                "program_id": active_phase.program.id,
                "exercise_id": workout_exercise.exercise.id,
            },
        )
        response = trainer_api_client.get(url, {"role": "ANTAGONIST"})
        assert response.status_code == 200
        entry = response.data[0]
        # No antagonist involvements in fixtures — should be empty
        assert entry["muscle_breakdown"] == []


class TestNextSessionRecommendationView:

    def test_trainer_can_get_recommendation(
        self,
        trainer_api_client,
        active_phase,
        workout_exercise,
        snapshot,
    ):
        url = reverse(
            "next-session-recommendation",
            kwargs={
                "program_id": active_phase.program.id,
                "exercise_id": workout_exercise.exercise.id,
            },
        )
        response = trainer_api_client.get(url)
        assert response.status_code == 200

    def test_response_includes_expected_fields(
        self,
        trainer_api_client,
        active_phase,
        workout_exercise,
        snapshot,
    ):
        url = reverse(
            "next-session-recommendation",
            kwargs={
                "program_id": active_phase.program.id,
                "exercise_id": workout_exercise.exercise.id,
            },
        )
        response = trainer_api_client.get(url)
        data = response.data
        assert "one_rep_max" in data
        assert "last_session_load" in data
        assert "target_load" in data
        assert "weight_floor" in data
        assert "weight_ceiling" in data
        assert "rep_range_min" in data
        assert "rep_range_max" in data
        assert "progression_cap_percent" in data

    def test_weight_floor_less_than_weight_ceiling(
        self,
        trainer_api_client,
        active_phase,
        workout_exercise,
        snapshot,
    ):
        url = reverse(
            "next-session-recommendation",
            kwargs={
                "program_id": active_phase.program.id,
                "exercise_id": workout_exercise.exercise.id,
            },
        )
        response = trainer_api_client.get(url)
        assert Decimal(response.data["weight_floor"]) < Decimal(
            response.data["weight_ceiling"]
        )

    def test_no_data_returns_204(
        self,
        trainer_api_client,
        active_phase,
        workout_exercise,
    ):
        url = reverse(
            "next-session-recommendation",
            kwargs={
                "program_id": active_phase.program.id,
                "exercise_id": workout_exercise.exercise.id,
            },
        )
        response = trainer_api_client.get(url)
        assert response.status_code == 204

    def test_client_cannot_access(
        self,
        client_api_client,
        active_phase,
        workout_exercise,
        snapshot,
    ):
        url = reverse(
            "next-session-recommendation",
            kwargs={
                "program_id": active_phase.program.id,
                "exercise_id": workout_exercise.exercise.id,
            },
        )
        response = client_api_client.get(url)
        assert response.status_code == 403

    def test_target_load_is_none_on_first_session(
        self,
        trainer_api_client,
        active_phase,
        workout_exercise,
        snapshot,
    ):
        """First session snapshot has no previous load so target_load is None."""
        url = reverse(
            "next-session-recommendation",
            kwargs={
                "program_id": active_phase.program.id,
                "exercise_id": workout_exercise.exercise.id,
            },
        )
        response = trainer_api_client.get(url)
        assert response.data["target_load"] is None
