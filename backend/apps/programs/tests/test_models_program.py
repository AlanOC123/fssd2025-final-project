from datetime import timedelta

import pytest
from django.core.exceptions import ValidationError
from django.utils import timezone

from factories import ProgramFactory, ProgramPhaseFactory

pytestmark = pytest.mark.django_db


def test_program_duration_properties_sum_phase_lengths(
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

    today = timezone.localdate()

    ProgramPhaseFactory(
        program=program,
        phase_option=program_phase_option_foundation,
        status=phase_status_planned,
        sequence_order=1,
        planned_start_date=today,
        planned_end_date=today + timedelta(days=14),
        created_by_trainer=trainer_user,
    )
    ProgramPhaseFactory(
        program=program,
        phase_option=program_phase_option_foundation,
        status=phase_status_planned,
        sequence_order=2,
        planned_start_date=today + timedelta(days=14),
        planned_end_date=today + timedelta(days=28),
        created_by_trainer=trainer_user,
    )

    assert program.program_duration_days == 28
    assert program.program_duration_weeks == 4


def test_program_has_created_phases_false_when_empty(
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

    assert program.has_created_phases is False


def test_program_has_created_phases_true_when_phases_exist(
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

    ProgramPhaseFactory(
        program=program,
        phase_option=program_phase_option_foundation,
        status=phase_status_planned,
        created_by_trainer=trainer_user,
    )

    assert program.has_created_phases is True


def test_program_phase_counts_and_all_finished_property(
    active_membership,
    training_goal_strength,
    experience_level_beginner,
    program_status_creating,
    phase_status_completed,
    phase_status_skipped,
    phase_status_archived,
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

    today = timezone.localdate()
    now = timezone.now()

    ProgramPhaseFactory(
        program=program,
        phase_option=program_phase_option_foundation,
        status=phase_status_completed,
        phase_goal="Complete block",
        actual_start_date=today,
        actual_end_date=today + timedelta(days=7),
        started_at=now,
        completed_at=now,
        created_by_trainer=trainer_user,
    )
    ProgramPhaseFactory(
        program=program,
        phase_option=program_phase_option_foundation,
        status=phase_status_skipped,
        sequence_order=2,
        skipped_at=now,
        skipped_reason="Injury flare-up",
        created_by_trainer=trainer_user,
    )
    ProgramPhaseFactory(
        program=program,
        phase_option=program_phase_option_foundation,
        status=phase_status_archived,
        sequence_order=3,
        archived_at=now,
        archived_reason="Program closed",
        created_by_trainer=trainer_user,
    )

    assert program.number_of_completed_phases == 1
    assert program.number_of_skipped_phases == 1
    assert program.number_of_archived_phases == 1
    assert program.all_phases_finished is True


def test_program_planned_and_actual_date_properties_follow_phase_order(
    active_membership,
    training_goal_strength,
    experience_level_beginner,
    program_status_in_progress,
    phase_status_completed,
    phase_status_active,
    program_phase_option_foundation,
    trainer_user,
):
    today = timezone.localdate()
    now = timezone.now()

    program = ProgramFactory(
        trainer_client_membership=active_membership,
        training_goal=training_goal_strength,
        experience_level=experience_level_beginner,
        status=program_status_in_progress,
        created_by_trainer=trainer_user,
        last_edited_by=trainer_user,
        submitted_for_review_at=now,
        reviewed_at=now,
        started_at=now,
    )

    ProgramPhaseFactory(
        program=program,
        phase_option=program_phase_option_foundation,
        status=phase_status_completed,
        sequence_order=1,
        planned_start_date=today,
        planned_end_date=today + timedelta(days=7),
        actual_start_date=today,
        actual_end_date=today + timedelta(days=7),
        started_at=now,
        completed_at=now,
        phase_goal="First block",
        created_by_trainer=trainer_user,
        last_edited_by=trainer_user,
    )

    ProgramPhaseFactory(
        program=program,
        phase_option=program_phase_option_foundation,
        status=phase_status_active,
        sequence_order=2,
        planned_start_date=today + timedelta(days=7),
        planned_end_date=today + timedelta(days=21),
        actual_start_date=today + timedelta(days=7),
        started_at=now,
        phase_goal="Second block",
        created_by_trainer=trainer_user,
        last_edited_by=trainer_user,
    )

    program.full_clean()

    assert program.planned_start_date == today
    assert program.planned_end_date == today + timedelta(days=21)
    assert program.actual_start_date == today
    assert program.actual_end_date is None


def test_program_version_must_be_greater_than_zero(
    active_membership,
    training_goal_strength,
    experience_level_beginner,
    program_status_creating,
    trainer_user,
):
    program = ProgramFactory.build(
        trainer_client_membership=active_membership,
        training_goal=training_goal_strength,
        experience_level=experience_level_beginner,
        status=program_status_creating,
        created_by_trainer=trainer_user,
        version=0,
    )

    with pytest.raises(ValidationError, match="version code"):
        program.full_clean()


def test_live_program_requires_created_by_trainer(
    active_membership,
    training_goal_strength,
    experience_level_beginner,
    program_status_ready,
):
    program = ProgramFactory.build(
        trainer_client_membership=active_membership,
        training_goal=training_goal_strength,
        experience_level=experience_level_beginner,
        status=program_status_ready,
        created_by_trainer=None,
    )

    with pytest.raises(ValidationError, match="record the trainer who created"):
        program.full_clean()


def test_live_program_requires_active_membership(
    pending_membership,
    training_goal_strength,
    experience_level_beginner,
    program_status_in_progress,
    trainer_user,
):
    now = timezone.now()

    program = ProgramFactory.build(
        trainer_client_membership=pending_membership,
        training_goal=training_goal_strength,
        experience_level=experience_level_beginner,
        status=program_status_in_progress,
        created_by_trainer=trainer_user,
        last_edited_by=trainer_user,
        submitted_for_review_at=now,
        reviewed_at=now,
        started_at=now,
    )

    with pytest.raises(ValidationError, match="active membership"):
        program.full_clean()


def test_only_trainers_can_create_programs(
    active_membership,
    training_goal_strength,
    experience_level_beginner,
    program_status_creating,
    client_user,
):
    program = ProgramFactory.build(
        trainer_client_membership=active_membership,
        training_goal=training_goal_strength,
        experience_level=experience_level_beginner,
        status=program_status_creating,
        created_by_trainer=client_user,
    )

    with pytest.raises(ValidationError, match="Only trainers can create programs"):
        program.full_clean()


def test_created_by_trainer_must_match_membership_trainer(
    active_membership,
    training_goal_strength,
    experience_level_beginner,
    program_status_creating,
    other_trainer_user,
):
    program = ProgramFactory.build(
        trainer_client_membership=active_membership,
        training_goal=training_goal_strength,
        experience_level=experience_level_beginner,
        status=program_status_creating,
        created_by_trainer=other_trainer_user,
    )

    with pytest.raises(ValidationError, match="associated with the membership"):
        program.full_clean()


def test_creating_program_cannot_have_review_submission_timestamp(
    active_membership,
    training_goal_strength,
    experience_level_beginner,
    program_status_creating,
    trainer_user,
):
    program = ProgramFactory.build(
        trainer_client_membership=active_membership,
        training_goal=training_goal_strength,
        experience_level=experience_level_beginner,
        status=program_status_creating,
        created_by_trainer=trainer_user,
        submitted_for_review_at=timezone.now(),
    )

    with pytest.raises(
        ValidationError,
        match="Draft programs cannot have a review submission timestamp",
    ):
        program.full_clean()


def test_ready_program_requires_submitted_for_review_at(
    active_membership,
    training_goal_strength,
    experience_level_beginner,
    program_status_review,
    trainer_user,
):
    program = ProgramFactory.build(
        trainer_client_membership=active_membership,
        training_goal=training_goal_strength,
        experience_level=experience_level_beginner,
        status=program_status_review,
        created_by_trainer=trainer_user,
        last_edited_by=trainer_user,
        submitted_for_review_at=None,
        reviewed_at=timezone.now(),
    )

    with pytest.raises(ValidationError):
        program.full_clean()


def test_ready_program_requires_reviewed_at(
    active_membership,
    training_goal_strength,
    experience_level_beginner,
    program_status_ready,
    trainer_user,
):
    program = ProgramFactory.build(
        trainer_client_membership=active_membership,
        training_goal=training_goal_strength,
        experience_level=experience_level_beginner,
        status=program_status_ready,
        created_by_trainer=trainer_user,
        submitted_for_review_at=timezone.now(),
        reviewed_at=None,
    )

    with pytest.raises(ValidationError, match="Reviewed programs must record"):
        program.full_clean()


def test_in_progress_program_requires_started_at(
    active_membership,
    training_goal_strength,
    experience_level_beginner,
    program_status_in_progress,
    trainer_user,
):
    program = ProgramFactory.build(
        trainer_client_membership=active_membership,
        training_goal=training_goal_strength,
        experience_level=experience_level_beginner,
        status=program_status_in_progress,
        created_by_trainer=trainer_user,
        submitted_for_review_at=timezone.now(),
        reviewed_at=timezone.now(),
        started_at=None,
    )

    with pytest.raises(ValidationError, match="Started programs must record"):
        program.full_clean()


def test_completed_program_requires_completed_at(
    active_membership,
    training_goal_strength,
    experience_level_beginner,
    program_status_completed,
    phase_status_active,
    program_phase_option_foundation,
    trainer_user,
):
    now = timezone.now()
    today = timezone.localdate()

    program = ProgramFactory(
        trainer_client_membership=active_membership,
        training_goal=training_goal_strength,
        experience_level=experience_level_beginner,
        status=program_status_completed,
        created_by_trainer=trainer_user,
        last_edited_by=trainer_user,
        submitted_for_review_at=now,
        reviewed_at=now,
        started_at=now,
        completed_at=now,
    )

    ProgramPhaseFactory(
        program=program,
        phase_option=program_phase_option_foundation,
        status=phase_status_active,
        phase_goal="Build base",
        actual_start_date=today,
        started_at=now,
        created_by_trainer=trainer_user,
        last_edited_by=trainer_user,
    )

    program.completed_at = None

    with pytest.raises(ValidationError):
        program.full_clean()


def test_abandoned_program_requires_abandoned_at(
    active_membership,
    training_goal_strength,
    experience_level_beginner,
    program_status_abandoned,
    trainer_user,
):
    now = timezone.now()

    program = ProgramFactory.build(
        trainer_client_membership=active_membership,
        training_goal=training_goal_strength,
        experience_level=experience_level_beginner,
        status=program_status_abandoned,
        created_by_trainer=trainer_user,
        submitted_for_review_at=now,
        reviewed_at=now,
        abandonment_reason="Client stopped responding",
        abandoned_at=None,
    )

    with pytest.raises(ValidationError):
        program.full_clean()


def test_program_cannot_be_completed_and_abandoned(
    active_membership,
    training_goal_strength,
    experience_level_beginner,
    program_status_completed,
    trainer_user,
):
    now = timezone.now()

    program = ProgramFactory.build(
        trainer_client_membership=active_membership,
        training_goal=training_goal_strength,
        experience_level=experience_level_beginner,
        status=program_status_completed,
        created_by_trainer=trainer_user,
        submitted_for_review_at=now,
        reviewed_at=now,
        started_at=now,
        completed_at=now,
        abandoned_at=now,
    )

    with pytest.raises(
        ValidationError,
        match="Programs cannot be both completed and abandoned",
    ):
        program.full_clean()


def test_program_string_includes_program_client_and_trainer_names(
    active_membership,
    training_goal_strength,
    experience_level_beginner,
    program_status_creating,
    trainer_user,
):
    program = ProgramFactory(
        program_name="Winter Arc",
        trainer_client_membership=active_membership,
        training_goal=training_goal_strength,
        experience_level=experience_level_beginner,
        status=program_status_creating,
        created_by_trainer=trainer_user,
    )

    result = str(program)

    assert "Winter Arc" in result
    assert active_membership.client.user.first_name in result
    assert active_membership.trainer.user.first_name in result
