# backend/tests/factories.py
# Shared factories used across multiple apps

from datetime import timedelta
from decimal import Decimal

import factory
from django.contrib.auth import get_user_model
from django.utils import timezone
from factory.django import DjangoModelFactory

from apps.programs.models import Program, ProgramPhase, ProgramPhaseOption
from apps.users.models import (
    ClientProfile,
    ExperienceLevel,
    TrainerClientMembership,
    TrainerProfile,
    TrainingGoal,
)
from apps.workouts.models import (
    Workout,
    WorkoutCompletionRecord,
    WorkoutExercise,
    WorkoutExerciseCompletionRecord,
    WorkoutSet,
    WorkoutSetCompletionRecord,
)

User = get_user_model()


class TrainingGoalFactory(DjangoModelFactory):
    class Meta:
        model = TrainingGoal
        django_get_or_create = ("code",)

    code = "STRENGTH"
    label = "Strength"


class ExperienceLevelFactory(DjangoModelFactory):
    class Meta:
        model = ExperienceLevel
        django_get_or_create = ("code",)

    code = "BEGINNER"
    label = "Beginner"


class TrainerUserFactory(DjangoModelFactory):
    class Meta:
        model = User

    email = factory.Faker("email")
    is_trainer = True
    is_client = False


class ClientUserFactory(DjangoModelFactory):
    class Meta:
        model = User

    email = factory.Faker("email")
    is_trainer = False
    is_client = True


class ProgramPhaseOptionFactory(DjangoModelFactory):
    class Meta:
        model = ProgramPhaseOption
        django_get_or_create = ("code",)

    code = "FOUNDATION"
    label = "Foundation"
    default_duration_days = 28


class ProgramFactory(DjangoModelFactory):
    class Meta:
        model = Program

    program_name = factory.Faker("sentence", nb_words=3)
    version = 1
    review_notes = ""
    completion_notes = ""
    abandonment_reason = ""


class ProgramPhaseFactory(DjangoModelFactory):
    class Meta:
        model = ProgramPhase

    phase_name = factory.Faker("sentence", nb_words=2)
    phase_goal = factory.Faker("sentence", nb_words=6)
    sequence_order = 1
    trainer_notes = factory.Faker("paragraph", nb_sentences=2)
    client_notes = ""
    planned_start_date = factory.LazyFunction(timezone.localdate)
    planned_end_date = factory.LazyFunction(
        lambda: timezone.localdate() + timedelta(days=28)
    )
    skipped_reason = ""
    archived_reason = ""


class WorkoutFactory(DjangoModelFactory):
    class Meta:
        model = Workout

    workout_name = factory.Faker("sentence", nb_words=3)
    planned_date = factory.LazyFunction(timezone.localdate)


class WorkoutExerciseFactory(DjangoModelFactory):
    class Meta:
        model = WorkoutExercise

    order = 1
    sets_prescribed = 3
    trainer_notes = ""


class WorkoutSetFactory(DjangoModelFactory):
    class Meta:
        model = WorkoutSet

    set_order = 1
    reps_prescribed = 5
    weight_prescribed = Decimal("100.00")


class WorkoutCompletionRecordFactory(DjangoModelFactory):
    class Meta:
        model = WorkoutCompletionRecord

    is_skipped = False
    started_at = factory.LazyFunction(timezone.now)
    completed_at = None


class WorkoutExerciseCompletionRecordFactory(DjangoModelFactory):
    class Meta:
        model = WorkoutExerciseCompletionRecord

    is_skipped = False
    started_at = factory.LazyFunction(timezone.now)
    completed_at = None


class WorkoutSetCompletionRecordFactory(DjangoModelFactory):
    class Meta:
        model = WorkoutSetCompletionRecord

    is_skipped = False
    completed_at = factory.LazyFunction(timezone.now)
    reps_completed = 5
    weight_completed = Decimal("100.00")
    difficulty_rating = None
    reps_in_reserve = None
