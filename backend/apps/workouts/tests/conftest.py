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
