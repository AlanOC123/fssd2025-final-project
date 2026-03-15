import pytest
from django.utils import timezone
from model_bakery import baker

from apps.programs.constants import (
    ProgramPhaseStatusesVocabulary,
    ProgramStatusesVocabulary,
)
from apps.programs.models import (
    ProgramPhaseOption,
    ProgramPhaseStatusOption,
    ProgramStatusOption,
)
from apps.users.models import ExperienceLevel, TrainingGoal
from apps.workouts.models import Workout, WorkoutExercise, WorkoutSet

pytestmark = pytest.mark.django_db


@pytest.fixture
def active_phase(active_membership):
    now = timezone.now()
    today = timezone.localdate()

    training_goal, _ = TrainingGoal.objects.get_or_create(
        code="STRENGTH_ANALYTICS",
        defaults={
            "label": "Strength",
            "rep_range_min": 1,
            "rep_range_max": 5,
        },
    )
    experience_level, _ = ExperienceLevel.objects.get_or_create(
        code="BEGINNER_ANALYTICS",
        defaults={
            "label": "Beginner",
            "progression_cap_percent": "0.15",
        },
    )
    program = baker.make(
        "programs.Program",
        trainer_client_membership=active_membership,
        training_goal=training_goal,
        experience_level=experience_level,
        status=ProgramStatusOption.objects.get(
            code=ProgramStatusesVocabulary.IN_PROGRESS
        ),
        created_by_trainer=active_membership.trainer.user,
        last_edited_by=active_membership.trainer.user,
        submitted_for_review_at=now,
        reviewed_at=now,
        started_at=now,
    )
    phase_option, _ = ProgramPhaseOption.objects.get_or_create(
        code="FOUNDATION", defaults={"label": "Foundation", "default_duration_days": 28}
    )
    return baker.make(
        "programs.ProgramPhase",
        program=program,
        phase_option=phase_option,
        status=ProgramPhaseStatusOption.objects.get(
            code=ProgramPhaseStatusesVocabulary.ACTIVE
        ),
        phase_goal="Build base strength",
        sequence_order=1,
        planned_start_date=today,
        planned_end_date=today + timezone.timedelta(days=28),
        actual_start_date=today,
        started_at=now,
        created_by_trainer=active_membership.trainer.user,
        last_edited_by=active_membership.trainer.user,
    )


@pytest.fixture
def exercise(level_beginner):
    from apps.exercises.models import Exercise

    exercise, _ = Exercise.objects.get_or_create(
        exercise_name="Barbell Back Squat",
        defaults={
            "api_name": "barbell_back_squat",
            "experience_level": level_beginner,
            "instructions": "Squat down",
            "safety_tips": "Keep back straight",
        },
    )
    return exercise


@pytest.fixture
def workout(active_phase):
    return baker.make(
        Workout,
        workout_name="Monday Lower",
        program_phase=active_phase,
        planned_date=timezone.localdate(),
    )


@pytest.fixture
def workout_exercise(workout, exercise):
    return baker.make(
        WorkoutExercise,
        workout=workout,
        exercise=exercise,
        order=1,
        sets_prescribed=3,
    )


@pytest.fixture
def workout_set(workout_exercise):
    return baker.make(
        WorkoutSet,
        workout_exercise=workout_exercise,
        set_order=1,
        reps_prescribed=5,
        weight_prescribed="100.00",
    )
