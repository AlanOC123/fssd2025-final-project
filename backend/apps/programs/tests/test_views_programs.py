import pytest
from django.urls import reverse
from django.utils import timezone

from factories import ProgramFactory, ProgramPhaseFactory

pytestmark = pytest.mark.django_db


def test_trainer_can_list_own_programs(
    trainer_api_client,
    active_membership,
    training_goal_strength,
    experience_level_beginner,
    program_status_creating,
    trainer_user,
):
    program = ProgramFactory(
        trainer_client_membership=active_membership,
        training_goal=training_goal_strength,
        experience_level=experience_level_beginner,
        status=program_status_creating,
        created_by_trainer=trainer_user,
    )

    url = reverse("programs-list")
    response = trainer_api_client.get(url)

    assert response.status_code == 200
    ids = [item["id"] for item in response.data["results"]]
    assert str(program.id) in ids


def test_client_can_list_own_programs(
    client_api_client,
    active_membership,
    training_goal_strength,
    experience_level_beginner,
    program_status_creating,
    trainer_user,
):
    program = ProgramFactory(
        trainer_client_membership=active_membership,
        training_goal=training_goal_strength,
        experience_level=experience_level_beginner,
        status=program_status_creating,
        created_by_trainer=trainer_user,
    )

    url = reverse("programs-list")
    response = client_api_client.get(url)

    assert response.status_code == 200
    ids = [item["id"] for item in response.data["results"]]
    assert str(program.id) in ids


def test_other_trainer_cannot_see_unrelated_program(
    other_trainer_api_client,
    active_membership,
    training_goal_strength,
    experience_level_beginner,
    program_status_creating,
    trainer_user,
):
    ProgramFactory(
        trainer_client_membership=active_membership,
        training_goal=training_goal_strength,
        experience_level=experience_level_beginner,
        status=program_status_creating,
        created_by_trainer=trainer_user,
    )

    url = reverse("programs-list")
    response = other_trainer_api_client.get(url)

    assert response.status_code == 200
    assert response.data["results"] == []


def test_trainer_can_create_program_for_own_membership(
    trainer_api_client,
    active_membership,
    training_goal_strength,
    experience_level_beginner,
):
    url = reverse("programs-list")
    payload = {
        "program_name": "Spring Build",
        "trainer_client_membership_id": str(active_membership.id),
        "training_goal_id": str(training_goal_strength.id),
        "experience_level_id": str(experience_level_beginner.id),
    }

    response = trainer_api_client.post(url, payload, format="json")

    assert response.status_code == 201
    assert response.data["program_name"] == "Spring Build"


def test_client_cannot_create_program(
    client_api_client,
    active_membership,
    training_goal_strength,
    experience_level_beginner,
):
    url = reverse("programs-list")
    payload = {
        "program_name": "Nope",
        "trainer_client_membership_id": str(active_membership.id),
        "training_goal_id": str(training_goal_strength.id),
        "experience_level_id": str(experience_level_beginner.id),
    }

    response = client_api_client.post(url, payload, format="json")

    assert response.status_code in {403, 400}


def test_trainer_can_submit_program_for_review(
    trainer_api_client,
    active_membership,
    training_goal_strength,
    experience_level_beginner,
    program_status_creating,
    program_phase_option_foundation,
    phase_status_planned,
    trainer_user,
):
    program = ProgramFactory(
        trainer_client_membership=active_membership,
        training_goal=training_goal_strength,
        experience_level=experience_level_beginner,
        status=program_status_creating,
        created_by_trainer=trainer_user,
        last_edited_by=trainer_user,
    )

    ProgramPhaseFactory(
        program=program,
        phase_option=program_phase_option_foundation,
        status=phase_status_planned,
        sequence_order=1,
        phase_name="Foundation",
        phase_goal="Build work capacity",
        created_by_trainer=trainer_user,
        last_edited_by=trainer_user,
    )

    url = reverse("programs-submit-for-review", args=[program.id])
    response = trainer_api_client.post(url, {}, format="json")

    assert response.status_code == 200
    assert response.data["status"]["label"] == "Out for Review"


def test_client_can_review_program(
    client_api_client,
    active_membership,
    training_goal_strength,
    experience_level_beginner,
    program_status_review,
    program_phase_option_foundation,
    phase_status_planned,
    trainer_user,
):
    now = timezone.now()

    program = ProgramFactory(
        trainer_client_membership=active_membership,
        training_goal=training_goal_strength,
        experience_level=experience_level_beginner,
        status=program_status_review,
        created_by_trainer=trainer_user,
        last_edited_by=trainer_user,
        submitted_for_review_at=now,
    )

    ProgramPhaseFactory(
        program=program,
        phase_option=program_phase_option_foundation,
        status=phase_status_planned,
        sequence_order=1,
        phase_name="Foundation",
        phase_goal="Build work capacity",
        created_by_trainer=trainer_user,
        last_edited_by=trainer_user,
    )

    url = reverse("programs-review", args=[program.id])
    payload = {
        "is_accepted": True,
        "feedback_notes": "Looks good",
    }
    response = client_api_client.post(url, payload, format="json")

    assert response.status_code == 200
    assert response.data["status"]["label"] == "Ready to Begin"


def test_client_can_start_ready_program(
    client_api_client,
    active_membership,
    training_goal_strength,
    experience_level_beginner,
    program_status_ready,
    program_phase_option_foundation,
    phase_status_next,
    trainer_user,
):
    now = timezone.now()

    program = ProgramFactory(
        trainer_client_membership=active_membership,
        training_goal=training_goal_strength,
        experience_level=experience_level_beginner,
        status=program_status_ready,
        created_by_trainer=trainer_user,
        last_edited_by=trainer_user,
        submitted_for_review_at=now,
        reviewed_at=now,
    )

    ProgramPhaseFactory(
        program=program,
        phase_option=program_phase_option_foundation,
        status=phase_status_next,
        sequence_order=1,
        phase_name="Foundation",
        phase_goal="Build work capacity",
        created_by_trainer=trainer_user,
        last_edited_by=trainer_user,
    )

    url = reverse("programs-start", args=[program.id])
    response = client_api_client.post(url, {}, format="json")

    assert response.status_code == 200
    assert response.data["status"]["label"] == "In Progress"


def test_complete_program_requires_notes(
    client_api_client,
    active_membership,
    training_goal_strength,
    experience_level_beginner,
    program_status_in_progress,
    trainer_user,
):
    now = timezone.now()

    program = ProgramFactory(
        trainer_client_membership=active_membership,
        training_goal=training_goal_strength,
        experience_level=experience_level_beginner,
        status=program_status_in_progress,
        created_by_trainer=trainer_user,
        submitted_for_review_at=now,
        reviewed_at=now,
        started_at=now,
    )

    url = reverse("programs-complete", args=[program.id])
    response = client_api_client.post(url, {}, format="json")

    assert response.status_code == 400


def test_client_can_abandon_program_with_reason(
    client_api_client,
    active_membership,
    training_goal_strength,
    experience_level_beginner,
    program_status_in_progress,
    trainer_user,
):
    now = timezone.now()

    program = ProgramFactory(
        trainer_client_membership=active_membership,
        training_goal=training_goal_strength,
        experience_level=experience_level_beginner,
        status=program_status_in_progress,
        created_by_trainer=trainer_user,
        submitted_for_review_at=now,
        reviewed_at=now,
        started_at=now,
    )

    url = reverse("programs-abandon", args=[program.id])
    payload = {"abandonment_reason": "Schedule collapsed"}
    response = client_api_client.post(url, payload, format="json")

    assert response.status_code == 200
    assert response.data["status"]["label"] == "Abandoned"
