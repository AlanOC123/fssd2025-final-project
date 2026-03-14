import pytest
from django.db import IntegrityError
from model_bakery import baker

from apps.biology.models import JointAction
from apps.exercises.models import (
    Exercise,
    ExerciseMovement,
    JointContribution,
    JointRangeOfMotion,
)

pytestmark = pytest.mark.django_db


def test_exercise_creation(
    dumbbell_bicep_curl_exercise, dumbbell_equipment, beginner_level
):
    assert dumbbell_bicep_curl_exercise.id is not None
    assert dumbbell_bicep_curl_exercise.exercise_name == "Dumbbell Bicep Curl"
    assert dumbbell_bicep_curl_exercise.equipment.contains(dumbbell_equipment)
    assert dumbbell_bicep_curl_exercise.instructions == "Curl the dumbbell upward."
    assert dumbbell_bicep_curl_exercise.safety_tips == "Keep elbows tucked."
    assert dumbbell_bicep_curl_exercise.experience_level == beginner_level
    assert str(dumbbell_bicep_curl_exercise) == "Dumbbell Bicep Curl"


def test_exercise_movement_creation(
    concentric_bicep_curl_movement, dumbbell_bicep_curl_exercise, concentric_phase
):
    assert concentric_bicep_curl_movement.phase == concentric_phase
    assert concentric_bicep_curl_movement.exercise == dumbbell_bicep_curl_exercise
    assert (
        str(concentric_bicep_curl_movement)
        == f"{concentric_phase.label} of {dumbbell_bicep_curl_exercise.exercise_name}"
    )


def test_joint_contribution_creation(
    elbow_flexion_joint_contribution,
    elbow_flexion_joint_action,
    full_range_of_motion,
    concentric_bicep_curl_movement,
):
    assert elbow_flexion_joint_contribution.joint_action == elbow_flexion_joint_action
    assert (
        elbow_flexion_joint_contribution.joint_range_of_motion == full_range_of_motion
    )
    assert (
        elbow_flexion_joint_contribution.exercise_movement
        == concentric_bicep_curl_movement
    )


def test_is_enriched_false_on_creation():
    exercise = baker.make(Exercise, instructions="", safety_tips="")

    assert exercise.is_enriched is False


def test_minimal_requirements_to_enrich_exercise(beginner_level):
    exercise = baker.prepare(
        Exercise, instructions="a", safety_tips="b", experience_level=beginner_level
    )

    assert exercise.is_enriched is False

    exercise.save()

    assert exercise.is_enriched is True


def test_unique_phase_per_exercise_movement_constraint(
    concentric_bicep_curl_movement,
    concentric_phase,
    dumbbell_bicep_curl_exercise,
):
    duplicate = baker.prepare(
        ExerciseMovement, phase=concentric_phase, exercise=dumbbell_bicep_curl_exercise
    )
    with pytest.raises(IntegrityError):
        duplicate.save()


def test_unique_exercise_movement_per_joint_action_constraint(
    elbow_flexion_joint_contribution,
    elbow_flexion_joint_action,
    concentric_bicep_curl_movement,
):
    duplicate = baker.prepare(
        JointContribution,
        exercise_movement=concentric_bicep_curl_movement,
        joint_action=elbow_flexion_joint_action,
    )
    with pytest.raises(IntegrityError):
        duplicate.save()


def test_joint_range_of_motion_impact_ordering(
    full_range_of_motion, partial_range_of_motion
):
    items = list(JointRangeOfMotion.objects.all())

    assert items[0] == full_range_of_motion
    assert items[1] == partial_range_of_motion


def test_joint_contribution_is_ordered_by_range_of_motion_impact_factor_desc(
    concentric_bicep_curl_movement, partial_range_of_motion, full_range_of_motion
):
    first_action = baker.make(JointAction)
    second_action = baker.make(JointAction)

    low = baker.make(
        JointContribution,
        exercise_movement=concentric_bicep_curl_movement,
        joint_action=first_action,
        joint_range_of_motion=partial_range_of_motion,
    )
    high = baker.make(
        JointContribution,
        exercise_movement=concentric_bicep_curl_movement,
        joint_action=second_action,
        joint_range_of_motion=full_range_of_motion,
    )

    items = list(JointContribution.objects.all())
    assert items[0] == high
    assert items[1] == low
