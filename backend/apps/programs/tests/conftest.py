import pytest

from apps.programs.constants import (
    ProgramPhaseStatusesVocabulary,
    ProgramStatusesVocabulary,
)
from apps.programs.models import ProgramPhaseStatusOption, ProgramStatusOption
from factories import (
    ExperienceLevelFactory,
    ProgramFactory,
    ProgramPhaseFactory,
    ProgramPhaseOptionFactory,
    TrainingGoalFactory,
)

pytestmark = pytest.mark.django_db


# ── Helpers ───────────────────────────────────────────────────────────────────
# Thin wrappers — vocab rows are guaranteed by seed_program_vocab (autouse).


def get_program_status(code):
    return ProgramStatusOption.objects.get(code=code)


def get_phase_status(code):
    return ProgramPhaseStatusOption.objects.get(code=code)


# ── Lookup fixtures ───────────────────────────────────────────────────────────


@pytest.fixture
def training_goal_strength():
    return TrainingGoalFactory(code="STRENGTH", label="Strength")


@pytest.fixture
def experience_level_beginner():
    return ExperienceLevelFactory(code="BEGINNER", label="Beginner")


@pytest.fixture
def program_phase_option_foundation():
    return ProgramPhaseOptionFactory()


# ── Program status fixtures ───────────────────────────────────────────────────


@pytest.fixture
def program_status_creating():
    return get_program_status(ProgramStatusesVocabulary.CREATING)


@pytest.fixture
def program_status_review():
    return get_program_status(ProgramStatusesVocabulary.REVIEW)


@pytest.fixture
def program_status_ready():
    return get_program_status(ProgramStatusesVocabulary.READY)


@pytest.fixture
def program_status_in_progress():
    return get_program_status(ProgramStatusesVocabulary.IN_PROGRESS)


@pytest.fixture
def program_status_completed():
    return get_program_status(ProgramStatusesVocabulary.COMPLETED)


@pytest.fixture
def program_status_abandoned():
    return get_program_status(ProgramStatusesVocabulary.ABANDONED)


# ── Phase status fixtures ─────────────────────────────────────────────────────


@pytest.fixture
def phase_status_planned():
    return get_phase_status(ProgramPhaseStatusesVocabulary.PLANNED)


@pytest.fixture
def phase_status_next():
    return get_phase_status(ProgramPhaseStatusesVocabulary.NEXT)


@pytest.fixture
def phase_status_active():
    return get_phase_status(ProgramPhaseStatusesVocabulary.ACTIVE)


@pytest.fixture
def phase_status_completed():
    return get_phase_status(ProgramPhaseStatusesVocabulary.COMPLETED)


@pytest.fixture
def phase_status_skipped():
    return get_phase_status(ProgramPhaseStatusesVocabulary.SKIPPED)


@pytest.fixture
def phase_status_archived():
    return get_phase_status(ProgramPhaseStatusesVocabulary.ARCHIVED)
