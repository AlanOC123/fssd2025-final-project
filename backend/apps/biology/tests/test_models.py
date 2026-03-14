from decimal import Decimal

import pytest
from django.core.exceptions import ValidationError
from django.db import IntegrityError
from model_bakery import baker

from apps.biology.models import (
    JointAction,
    MovementPattern,
    MuscleInvolvement,
)

pytestmark = pytest.mark.django_db


def test_joint_action_creation(
    elbow_flexion_joint_action, elbow_joint, flexion_movement, sagittal_plane
):
    assert elbow_flexion_joint_action.id is not None
    assert elbow_flexion_joint_action.joint == elbow_joint
    assert elbow_flexion_joint_action.movement == flexion_movement
    assert elbow_flexion_joint_action.plane == sagittal_plane


def test_muscle_involvement_creations(
    bicep_elbow_flexion_involvement,
    bicep_muscle,
    elbow_flexion_joint_action,
    agonist_role,
):
    assert bicep_elbow_flexion_involvement.id is not None
    assert bicep_elbow_flexion_involvement.muscle == bicep_muscle
    assert bicep_elbow_flexion_involvement.joint_action == elbow_flexion_joint_action
    assert bicep_elbow_flexion_involvement.role == agonist_role
    assert bicep_elbow_flexion_involvement.impact_factor == Decimal("0.80")


def test_joint_action_enforces_unique_joint_movement(
    elbow_joint, flexion_movement, sagittal_plane
):
    baker.make(
        JointAction,
        joint=elbow_joint,
        movement=flexion_movement,
        plane=sagittal_plane,
    )

    duplicate = baker.prepare(
        JointAction,
        joint=elbow_joint,
        movement=flexion_movement,
        plane=sagittal_plane,
    )

    with pytest.raises(IntegrityError):
        duplicate.save()


def test_muscle_involvement_enforces_unique_muscle_joint_action(
    bicep_muscle,
    bicep_elbow_flexion_involvement,
    elbow_flexion_joint_action,
    agonist_role,
):
    # Row already exists via bicep_elbow_flexion_involvement fixture.
    # Attempting to save a duplicate should raise a ValidationError.
    duplicate = baker.prepare(
        MuscleInvolvement,
        muscle=bicep_muscle,
        joint_action=elbow_flexion_joint_action,
        role=agonist_role,
        impact_factor=Decimal("0.80"),
    )

    with pytest.raises(ValidationError):
        duplicate.save()


def test_joint_action_allows_same_joint_with_different_movement(
    elbow_joint,
    sagittal_plane,
    flexion_movement,
    extension_movement,
):
    first = baker.make(
        JointAction,
        joint=elbow_joint,
        movement=flexion_movement,
        plane=sagittal_plane,
    )
    second = baker.make(
        JointAction,
        joint=elbow_joint,
        movement=extension_movement,
        plane=sagittal_plane,
    )
    assert first.id is not None
    assert second.id is not None


@pytest.mark.parametrize("impact_factor", [Decimal("-1.00"), Decimal("2.00")])
def test_muscle_involvement_rejects_impact_factor_invalid_values(impact_factor):
    muscle_involvement = baker.prepare(MuscleInvolvement, impact_factor=impact_factor)

    with pytest.raises(ValidationError):
        muscle_involvement.save()


@pytest.mark.parametrize("edge_impact_factor", [Decimal("0.01"), Decimal("0.99")])
def test_muscle_involvement_accepts_edge_impact_factor_values(edge_impact_factor):
    muscle_involvement = baker.make(MuscleInvolvement, impact_factor=edge_impact_factor)

    assert muscle_involvement.id is not None
    assert muscle_involvement.impact_factor == edge_impact_factor
