import pytest
from django.contrib.auth import get_user_model

from apps.users.models import (
    TrainerProfile,
)

User = get_user_model()
pytestmark = pytest.mark.django_db


def test_client_constraints_single_selection(
    client, goal_strength, goal_muscle_mass, level_beginner, level_intermediate
):
    client.goal = goal_strength
    client.level = level_beginner
    client.save()

    assert client.goal == goal_strength
    assert client.level == level_beginner

    client.goal = goal_muscle_mass
    client.level = level_intermediate
    client.save()

    assert client.goal == goal_muscle_mass
    assert client.level == level_intermediate


def test_trainer_constraints_many_selections(
    trainer_a,
    goal_strength,
    goal_muscle_mass,
    level_beginner,
    level_intermediate,
):
    trainer_a.accepted_goals.add(goal_strength, goal_muscle_mass)
    trainer_a.accepted_levels.add(level_beginner, level_intermediate)

    assert trainer_a.accepted_goals.count() == 2
    assert trainer_a.accepted_levels.count() == 2

    assert goal_muscle_mass in trainer_a.accepted_goals.all()
    assert level_intermediate in trainer_a.accepted_levels.all()


def test_matching_logic(
    client_strength_beginner,
    trainer_a_strength_beginner,
    trainer_b_muscle_mass_beginner,
):
    matches = TrainerProfile.objects.filter(
        accepted_goals=client_strength_beginner.goal,
        accepted_levels=client_strength_beginner.level,
    ).distinct()

    assert trainer_a_strength_beginner in matches
    assert trainer_b_muscle_mass_beginner not in matches


def test_client_has_choice_of_trainers(
    client_strength_beginner,
    trainer_a_strength_beginner,
    trainer_c_strength_intermediate,
    trainer_d_strength_beginner,
):
    matches = TrainerProfile.objects.filter(
        accepted_goals=client_strength_beginner.goal,
        accepted_levels=client_strength_beginner.level,
    ).distinct()

    assert trainer_a_strength_beginner in matches
    assert trainer_d_strength_beginner in matches
    assert trainer_c_strength_intermediate not in matches
