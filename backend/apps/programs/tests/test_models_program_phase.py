from datetime import timedelta

import pytest
from django.core.exceptions import ValidationError
from django.utils import timezone

from factories import ProgramFactory, ProgramPhaseFactory

pytestmark = pytest.mark.django_db


def test_phase_duration_properties(
    active_membership,
    training_goal_strength,
    experience_level_beginner,
    program_status_creating,
    phase_status_planned,
    program_phase_option_foundation,
    trainer_user,
):
    today = timezone.localdate()

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
        planned_start_date=today,
        planned_end_date=today + timedelta(days=15),
        created_by_trainer=trainer_user,
    )

    assert phase.duration_days == 15
    assert phase.duration_weeks == 3


def test_sequence_order_must_be_greater_than_zero(
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

    phase = ProgramPhaseFactory.build(
        program=program,
        phase_option=program_phase_option_foundation,
        status=phase_status_planned,
        sequence_order=0,
        created_by_trainer=trainer_user,
    )

    with pytest.raises(ValidationError, match="sequence order must be greater than 0"):
        phase.full_clean()


def test_planned_start_must_be_before_planned_end(
    active_membership,
    training_goal_strength,
    experience_level_beginner,
    program_status_creating,
    phase_status_planned,
    program_phase_option_foundation,
    trainer_user,
):
    today = timezone.localdate()

    program = ProgramFactory(
        trainer_client_membership=active_membership,
        training_goal=training_goal_strength,
        experience_level=experience_level_beginner,
        status=program_status_creating,
        created_by_trainer=trainer_user,
    )

    phase = ProgramPhaseFactory.build(
        program=program,
        phase_option=program_phase_option_foundation,
        status=phase_status_planned,
        planned_start_date=today,
        planned_end_date=today,
        created_by_trainer=trainer_user,
    )

    with pytest.raises(
        ValidationError,
        match="Planned start date must be before planned end date",
    ):
        phase.full_clean()


def test_actual_start_cannot_be_after_actual_end(
    active_membership,
    training_goal_strength,
    experience_level_beginner,
    program_status_creating,
    phase_status_planned,
    program_phase_option_foundation,
    trainer_user,
):
    today = timezone.localdate()

    program = ProgramFactory(
        trainer_client_membership=active_membership,
        training_goal=training_goal_strength,
        experience_level=experience_level_beginner,
        status=program_status_creating,
        created_by_trainer=trainer_user,
    )

    phase = ProgramPhaseFactory.build(
        program=program,
        phase_option=program_phase_option_foundation,
        status=phase_status_planned,
        actual_start_date=today + timedelta(days=10),
        actual_end_date=today,
        created_by_trainer=trainer_user,
    )

    with pytest.raises(
        ValidationError,
        match="Actual start date cannot be after actual end date",
    ):
        phase.full_clean()


def test_started_at_requires_actual_start_date(
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

    phase = ProgramPhaseFactory.build(
        program=program,
        phase_option=program_phase_option_foundation,
        status=phase_status_planned,
        actual_start_date=None,
        started_at=timezone.now(),
        created_by_trainer=trainer_user,
    )

    with pytest.raises(ValidationError, match="must record an actual start date"):
        phase.full_clean()


def test_completed_at_requires_actual_end_date(
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

    phase = ProgramPhaseFactory.build(
        program=program,
        phase_option=program_phase_option_foundation,
        status=phase_status_planned,
        actual_end_date=None,
        completed_at=timezone.now(),
        created_by_trainer=trainer_user,
    )

    with pytest.raises(ValidationError, match="must record an actual end date"):
        phase.full_clean()


def test_active_phase_requires_goal_actual_start_and_started_at(
    active_membership,
    training_goal_strength,
    experience_level_beginner,
    program_status_in_progress,
    phase_status_active,
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

    phase = ProgramPhaseFactory.build(
        program=program,
        phase_option=program_phase_option_foundation,
        status=phase_status_active,
        phase_goal="",
        actual_start_date=None,
        started_at=None,
        created_by_trainer=trainer_user,
    )

    with pytest.raises(ValidationError):
        phase.full_clean()


def test_completed_phase_requires_completion_metadata(
    active_membership,
    training_goal_strength,
    experience_level_beginner,
    program_status_in_progress,
    phase_status_completed,
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
        submitted_for_review_at=now,
        reviewed_at=now,
        started_at=now,
    )

    phase = ProgramPhaseFactory.build(
        program=program,
        phase_option=program_phase_option_foundation,
        status=phase_status_completed,
        phase_goal="Build base",
        actual_start_date=today,
        actual_end_date=today + timedelta(days=14),
        started_at=now,
        completed_at=None,
        created_by_trainer=trainer_user,
    )

    with pytest.raises(ValidationError, match="record when they were completed"):
        phase.full_clean()


def test_skipped_phase_requires_reason_and_timestamp(
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

    phase = ProgramPhaseFactory.build(
        program=program,
        phase_option=program_phase_option_foundation,
        status=phase_status_skipped,
        skipped_at=None,
        skipped_reason="",
        created_by_trainer=trainer_user,
    )

    with pytest.raises(ValidationError):
        phase.full_clean()


def test_archived_phase_requires_reason_and_timestamp(
    active_membership,
    training_goal_strength,
    experience_level_beginner,
    program_status_abandoned,
    phase_status_archived,
    program_phase_option_foundation,
    trainer_user,
):
    now = timezone.now()

    program = ProgramFactory(
        trainer_client_membership=active_membership,
        training_goal=training_goal_strength,
        experience_level=experience_level_beginner,
        status=program_status_abandoned,
        created_by_trainer=trainer_user,
        last_edited_by=trainer_user,
        submitted_for_review_at=now,
        reviewed_at=now,
        started_at=now,
        abandoned_at=now,
        abandonment_reason="Membership became inactive.",
    )

    phase = ProgramPhaseFactory.build(
        program=program,
        phase_option=program_phase_option_foundation,
        status=phase_status_archived,
        archived_at=None,
        archived_reason="",
        created_by_trainer=trainer_user,
        last_edited_by=trainer_user,
    )

    with pytest.raises(ValidationError):
        phase.full_clean()


def test_skipped_reason_only_allowed_on_skipped_phase(
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

    phase = ProgramPhaseFactory.build(
        program=program,
        phase_option=program_phase_option_foundation,
        status=phase_status_planned,
        skipped_reason="No longer needed",
        created_by_trainer=trainer_user,
    )

    with pytest.raises(ValidationError, match="Skipped reason can only be tracked"):
        phase.full_clean()


def test_archived_reason_only_allowed_on_archived_phase(
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

    phase = ProgramPhaseFactory.build(
        program=program,
        phase_option=program_phase_option_foundation,
        status=phase_status_planned,
        archived_reason="Program ended",
        created_by_trainer=trainer_user,
    )

    with pytest.raises(ValidationError, match="Archived reason can only be tracked"):
        phase.full_clean()


def test_completed_and_skipped_timestamps_cannot_coexist(
    active_membership,
    training_goal_strength,
    experience_level_beginner,
    program_status_creating,
    phase_status_completed,
    program_phase_option_foundation,
    trainer_user,
):
    today = timezone.localdate()
    now = timezone.now()

    program = ProgramFactory(
        trainer_client_membership=active_membership,
        training_goal=training_goal_strength,
        experience_level=experience_level_beginner,
        status=program_status_creating,
        created_by_trainer=trainer_user,
    )

    phase = ProgramPhaseFactory.build(
        program=program,
        phase_option=program_phase_option_foundation,
        status=phase_status_completed,
        phase_goal="Close block",
        actual_start_date=today,
        actual_end_date=today + timedelta(days=7),
        started_at=now,
        completed_at=now,
        skipped_at=now,
        created_by_trainer=trainer_user,
    )

    with pytest.raises(
        ValidationError,
    ):
        phase.full_clean()


def test_only_trainers_can_create_program_phases(
    active_membership,
    training_goal_strength,
    experience_level_beginner,
    program_status_creating,
    phase_status_planned,
    program_phase_option_foundation,
    client_user,
):
    program = ProgramFactory(
        trainer_client_membership=active_membership,
        training_goal=training_goal_strength,
        experience_level=experience_level_beginner,
        status=program_status_creating,
        created_by_trainer=active_membership.trainer.user,
    )

    phase = ProgramPhaseFactory.build(
        program=program,
        phase_option=program_phase_option_foundation,
        status=phase_status_planned,
        created_by_trainer=client_user,
    )

    with pytest.raises(
        ValidationError,
        match="Program phases can only be created by trainers",
    ):
        phase.full_clean()


def test_sequence_order_must_be_unique_within_program(
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
        sequence_order=1,
        created_by_trainer=trainer_user,
    )

    duplicate = ProgramPhaseFactory.build(
        program=program,
        phase_option=program_phase_option_foundation,
        status=phase_status_planned,
        sequence_order=1,
        created_by_trainer=trainer_user,
    )

    with pytest.raises(ValidationError):
        duplicate.full_clean()


def test_phase_string_uses_name_or_phase_option_label(
    active_membership,
    training_goal_strength,
    experience_level_beginner,
    program_status_creating,
    phase_status_planned,
    program_phase_option_foundation,
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

    phase = ProgramPhaseFactory(
        program=program,
        phase_option=program_phase_option_foundation,
        status=phase_status_planned,
        phase_name="Foundation Block",
        created_by_trainer=trainer_user,
    )

    result = str(phase)

    assert "Foundation Block" in result
    assert "Winter Arc" in result
