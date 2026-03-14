import pytest
from django.urls import reverse
from django.utils import timezone

from factories import ProgramFactory, ProgramPhaseFactory

pytestmark = pytest.mark.django_db


def test_trainer_can_list_own_program_phases(
    trainer_api_client,
    active_membership,
    training_goal_strength,
    experience_level_beginner,
    program_status_creating,
    phase_status_planned,
    program_phase_option_foundation,
    trainer_user,
):
    program = ProgramFactory(
        trainer_client_membership=active_membership,
        training_goal=training_goal_strength,
        experience_level=experience_level_beginner,
        status=program_status_creating,
        created_by_trainer=trainer_user,
    )

    phase = ProgramPhaseFactory(
        program=program,
        phase_option=program_phase_option_foundation,
        status=phase_status_planned,
        created_by_trainer=trainer_user,
    )

    url = reverse("program-phases-list")
    response = trainer_api_client.get(url)

    assert response.status_code == 200
    ids = [item["id"] for item in response.data]
    assert str(phase.id) in ids


def test_client_can_list_own_program_phases(
    client_api_client,
    active_membership,
    training_goal_strength,
    experience_level_beginner,
    program_status_creating,
    phase_status_planned,
    program_phase_option_foundation,
    trainer_user,
):
    program = ProgramFactory(
        trainer_client_membership=active_membership,
        training_goal=training_goal_strength,
        experience_level=experience_level_beginner,
        status=program_status_creating,
        created_by_trainer=trainer_user,
    )

    phase = ProgramPhaseFactory(
        program=program,
        phase_option=program_phase_option_foundation,
        status=phase_status_planned,
        created_by_trainer=trainer_user,
    )

    url = reverse("program-phases-list")
    response = client_api_client.get(url)

    assert response.status_code == 200
    ids = [item["id"] for item in response.data]
    assert str(phase.id) in ids


def test_trainer_can_create_program_phase(
    trainer_api_client,
    active_membership,
    training_goal_strength,
    experience_level_beginner,
    program_status_creating,
    phase_status_planned,
    program_phase_option_foundation,
    trainer_user,
):
    program = ProgramFactory(
        trainer_client_membership=active_membership,
        training_goal=training_goal_strength,
        experience_level=experience_level_beginner,
        status=program_status_creating,
        created_by_trainer=trainer_user,
    )

    url = reverse("program-phases-list")
    payload = {
        "program_id": str(program.id),
        "phase_option_id": str(program_phase_option_foundation.id),
        "phase_name": "Foundation",
        "phase_goal": "Build work capacity",
        "sequence_order": 1,
        "trainer_notes": "Start steady",
        "client_notes": "",
        "planned_start_date": str(timezone.localdate()),
        "planned_end_date": str(timezone.localdate() + timezone.timedelta(days=14)),
    }

    response = trainer_api_client.post(url, payload, format="json")

    assert response.status_code == 201
    assert response.data["phase_name"] == "Foundation"


def test_client_cannot_create_program_phase(
    client_api_client,
    active_membership,
    training_goal_strength,
    experience_level_beginner,
    program_status_creating,
    program_phase_option_foundation,
    trainer_user,
):
    program = ProgramFactory(
        trainer_client_membership=active_membership,
        training_goal=training_goal_strength,
        experience_level=experience_level_beginner,
        status=program_status_creating,
        created_by_trainer=trainer_user,
    )

    url = reverse("program-phases-list")
    payload = {
        "program_id": str(program.id),
        "phase_option_id": str(program_phase_option_foundation.id),
        "phase_name": "Nope",
        "phase_goal": "Nope",
        "sequence_order": 1,
        "planned_start_date": str(timezone.localdate()),
        "planned_end_date": str(timezone.localdate() + timezone.timedelta(days=14)),
    }

    response = client_api_client.post(url, payload, format="json")

    assert response.status_code in {403, 400}


def test_trainer_can_mark_phase_as_next(
    trainer_api_client,
    active_membership,
    training_goal_strength,
    experience_level_beginner,
    program_status_creating,
    phase_status_planned,
    program_phase_option_foundation,
    trainer_user,
):
    program = ProgramFactory(
        trainer_client_membership=active_membership,
        training_goal=training_goal_strength,
        experience_level=experience_level_beginner,
        status=program_status_creating,
        created_by_trainer=trainer_user,
    )

    phase = ProgramPhaseFactory(
        program=program,
        phase_option=program_phase_option_foundation,
        status=phase_status_planned,
        sequence_order=1,
        created_by_trainer=trainer_user,
    )

    url = reverse("program-phases-mark-next", args=[phase.id])
    response = trainer_api_client.post(url, {}, format="json")

    assert response.status_code == 200
    assert response.data["status"]["label"] == "Next"


def test_trainer_can_activate_next_phase(
    trainer_api_client,
    active_membership,
    training_goal_strength,
    experience_level_beginner,
    program_status_in_progress,
    phase_status_next,
    program_phase_option_foundation,
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

    phase = ProgramPhaseFactory(
        program=program,
        phase_option=program_phase_option_foundation,
        status=phase_status_next,
        sequence_order=1,
        phase_goal="Build work capacity",
        created_by_trainer=trainer_user,
    )

    url = reverse("program-phases-activate", args=[phase.id])
    response = trainer_api_client.post(url, {}, format="json")

    assert response.status_code == 200
    assert response.data["status"]["label"] == "Active"


def test_skip_phase_requires_reason(
    trainer_api_client,
    active_membership,
    training_goal_strength,
    experience_level_beginner,
    program_status_creating,
    phase_status_planned,
    program_phase_option_foundation,
    trainer_user,
):
    program = ProgramFactory(
        trainer_client_membership=active_membership,
        training_goal=training_goal_strength,
        experience_level=experience_level_beginner,
        status=program_status_creating,
        created_by_trainer=trainer_user,
    )

    phase = ProgramPhaseFactory(
        program=program,
        phase_option=program_phase_option_foundation,
        status=phase_status_planned,
        created_by_trainer=trainer_user,
    )

    url = reverse("program-phases-skip", args=[phase.id])
    response = trainer_api_client.post(url, {}, format="json")

    assert response.status_code == 400


def test_trainer_can_skip_phase_with_reason(
    trainer_api_client,
    active_membership,
    training_goal_strength,
    experience_level_beginner,
    program_status_creating,
    phase_status_planned,
    program_phase_option_foundation,
    trainer_user,
):
    program = ProgramFactory(
        trainer_client_membership=active_membership,
        training_goal=training_goal_strength,
        experience_level=experience_level_beginner,
        status=program_status_creating,
        created_by_trainer=trainer_user,
    )

    phase = ProgramPhaseFactory(
        program=program,
        phase_option=program_phase_option_foundation,
        status=phase_status_planned,
        created_by_trainer=trainer_user,
    )

    url = reverse("program-phases-skip", args=[phase.id])
    payload = {"reason": "Need to reorder blocks"}
    response = trainer_api_client.post(url, payload, format="json")

    assert response.status_code == 200
    assert response.data["status"]["label"] == "Skipped"
    assert response.data["skipped_reason"] == "Need to reorder blocks"


def test_trainer_can_restore_skipped_phase_to_planned(
    trainer_api_client,
    active_membership,
    training_goal_strength,
    experience_level_beginner,
    program_status_creating,
    phase_status_skipped,
    program_phase_option_foundation,
    trainer_user,
):
    program = ProgramFactory(
        trainer_client_membership=active_membership,
        training_goal=training_goal_strength,
        experience_level=experience_level_beginner,
        status=program_status_creating,
        created_by_trainer=trainer_user,
    )

    phase = ProgramPhaseFactory(
        program=program,
        phase_option=program_phase_option_foundation,
        status=phase_status_skipped,
        skipped_at=timezone.now(),
        skipped_reason="Temporary reorder",
        created_by_trainer=trainer_user,
    )

    url = reverse("program-phases-restore-to-planned", args=[phase.id])
    response = trainer_api_client.post(url, {}, format="json")

    assert response.status_code == 200
    assert response.data["status"]["label"] == "Next"
