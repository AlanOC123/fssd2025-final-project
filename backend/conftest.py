from decimal import Decimal

import pytest
from django.contrib.auth import get_user_model
from django.utils import timezone
from model_bakery import baker
from rest_framework.test import APIClient

from apps.biology.constants import (
    AnatomicalDirectionVocabulary,
    JointVocabulary,
    MovementPatternVocabulary,
    MuscleGroupVocabulary,
    MuscleRoleVocabulary,
    PlaneOfMotionVocabulary,
)
from apps.biology.models import (
    AnatomicalDirection,
    Joint,
    JointAction,
    MovementPattern,
    Muscle,
    MuscleGroup,
    MuscleInvolvement,
    MuscleRole,
    PlaneOfMotion,
)
from apps.exercises.constants import (
    ExercisePhaseVocabulary,
    JointRangeOfMotionVocabulary,
)
from apps.exercises.models import (
    Equipment,
    Exercise,
    ExerciseMovement,
    ExercisePhase,
    JointContribution,
    JointRangeOfMotion,
)
from apps.programs.constants import (
    ProgramPhaseStatusesVocabulary,
    ProgramStatusesVocabulary,
)
from apps.programs.models import (
    ProgramPhaseStatusOption,
    ProgramStatusOption,
)
from apps.users.constants import MembershipVocabulary
from apps.users.models import (
    ExperienceLevel,
    MembershipStatus,
    TrainerClientMembership,
    TrainingGoal,
)

User = get_user_model()


# ── Vocabulary seeding ────────────────────────────────────────────────────────


@pytest.fixture(autouse=True)
def seed_program_vocab(db):
    for code, label in [
        (ProgramStatusesVocabulary.CREATING, "Creating"),
        (ProgramStatusesVocabulary.REVIEW, "Out for Review"),
        (ProgramStatusesVocabulary.READY, "Ready to Begin"),
        (ProgramStatusesVocabulary.IN_PROGRESS, "In Progress"),
        (ProgramStatusesVocabulary.COMPLETED, "Completed"),
        (ProgramStatusesVocabulary.ABANDONED, "Abandoned"),
    ]:
        ProgramStatusOption.objects.get_or_create(code=code, defaults={"label": label})

    for code, label in [
        (ProgramPhaseStatusesVocabulary.PLANNED, "Planned"),
        (ProgramPhaseStatusesVocabulary.NEXT, "Next"),
        (ProgramPhaseStatusesVocabulary.ACTIVE, "Active"),
        (ProgramPhaseStatusesVocabulary.COMPLETED, "Completed"),
        (ProgramPhaseStatusesVocabulary.SKIPPED, "Skipped"),
        (ProgramPhaseStatusesVocabulary.ARCHIVED, "Archived"),
    ]:
        ProgramPhaseStatusOption.objects.get_or_create(
            code=code, defaults={"label": label}
        )

    for code, label in [
        (MembershipVocabulary.PENDING, "Pending Trainer Review"),
        (MembershipVocabulary.ACTIVE, "Active"),
        (MembershipVocabulary.REJECTED, "Rejected"),
        (MembershipVocabulary.DISSOLVED_BY_CLIENT, "Dissolved by Client"),
        (MembershipVocabulary.DISSOLVED_BY_TRAINER, "Dissolved by Trainer"),
    ]:
        MembershipStatus.objects.get_or_create(code=code, defaults={"label": label})


# ── API helpers ───────────────────────────────────────────────────────────────


@pytest.fixture
def api_client():
    return APIClient()


@pytest.fixture
def response_items():
    def extract(response):
        data = response.data
        if "results" in data:
            return response.status_code, data["results"]
        return response.status_code, data

    return extract


# ── Users ─────────────────────────────────────────────────────────────────────


@pytest.fixture
def trainer_user():
    return baker.make(
        User, is_trainer=True, is_client=False, email="trainer@example.com"
    )


@pytest.fixture
def client_user():
    return baker.make(
        User, is_trainer=False, is_client=True, email="client@example.com"
    )


@pytest.fixture
def other_trainer_user():
    return baker.make(
        User, is_trainer=True, is_client=False, email="other-trainer@example.com"
    )


@pytest.fixture
def other_client_user():
    return baker.make(
        User, is_trainer=False, is_client=True, email="other-client@example.com"
    )


@pytest.fixture
def trainer_profile(trainer_user):
    return trainer_user.trainer_profile


@pytest.fixture
def client_profile(client_user):
    return client_user.client_profile


# ── Authenticated API clients ─────────────────────────────────────────────────


@pytest.fixture
def trainer_api_client(api_client, trainer_user):
    api_client.force_authenticate(user=trainer_user)
    return api_client


@pytest.fixture
def client_api_client(api_client, client_user):
    api_client.force_authenticate(user=client_user)
    return api_client


@pytest.fixture
def other_trainer_api_client(api_client, other_trainer_user):
    api_client.force_authenticate(user=other_trainer_user)
    return api_client


# ── Membership ────────────────────────────────────────────────────────────────


@pytest.fixture
def active_membership(trainer_profile, client_profile):
    now = timezone.now()
    status = MembershipStatus.objects.get(code=MembershipVocabulary.ACTIVE)
    return baker.make(
        TrainerClientMembership,
        trainer=trainer_profile,
        client=client_profile,
        status=status,
        responded_at=now,
        started_at=now,
    )


@pytest.fixture
def pending_membership(trainer_profile, client_profile):
    status = MembershipStatus.objects.get(code=MembershipVocabulary.PENDING)
    return baker.make(
        TrainerClientMembership,
        trainer=trainer_profile,
        client=client_profile,
        status=status,
    )


# ── Experience levels ─────────────────────────────────────────────────────────


@pytest.fixture
def level_beginner():
    obj, _ = ExperienceLevel.objects.get_or_create(
        code="BEGINNER", defaults={"label": "Beginner"}
    )
    return obj


@pytest.fixture
def level_intermediate():
    obj, _ = ExperienceLevel.objects.get_or_create(
        code="INTERMEDIATE", defaults={"label": "Intermediate"}
    )
    return obj


@pytest.fixture
def level_advanced():
    obj, _ = ExperienceLevel.objects.get_or_create(
        code="ADVANCED", defaults={"label": "Advanced"}
    )
    return obj


# ── Training goals ────────────────────────────────────────────────────────────


@pytest.fixture
def goal_strength():
    obj, _ = TrainingGoal.objects.get_or_create(
        code="STRENGTH", defaults={"label": "Strength"}
    )
    return obj


@pytest.fixture
def goal_hypertrophy():
    obj, _ = TrainingGoal.objects.get_or_create(
        code="HYPERTROPHY", defaults={"label": "Hypertrophy"}
    )
    return obj


# ── Biology lookups ───────────────────────────────────────────────────────────


@pytest.fixture
def sagittal_plane():
    obj, _ = PlaneOfMotion.objects.get_or_create(
        code=PlaneOfMotionVocabulary.SAGITTAL, defaults={"label": "Sagittal"}
    )
    return obj


@pytest.fixture
def transverse_plane():
    obj, _ = PlaneOfMotion.objects.get_or_create(
        code=PlaneOfMotionVocabulary.TRANSVERSE, defaults={"label": "Transverse"}
    )
    return obj


@pytest.fixture
def frontal_plane():
    obj, _ = PlaneOfMotion.objects.get_or_create(
        code=PlaneOfMotionVocabulary.FRONTAL, defaults={"label": "Frontal"}
    )
    return obj


@pytest.fixture
def elbow_joint():
    obj, _ = Joint.objects.get_or_create(
        code=JointVocabulary.ELBOW, defaults={"label": "Elbow"}
    )
    return obj


@pytest.fixture
def shoulder_joint():
    obj, _ = Joint.objects.get_or_create(
        code=JointVocabulary.SHOULDER, defaults={"label": "Shoulder"}
    )
    return obj


@pytest.fixture
def flexion_movement():
    obj, _ = MovementPattern.objects.get_or_create(
        code=MovementPatternVocabulary.FLEXION, defaults={"label": "Flexion"}
    )
    return obj


@pytest.fixture
def extension_movement():
    obj, _ = MovementPattern.objects.get_or_create(
        code=MovementPatternVocabulary.EXTENSION, defaults={"label": "Extension"}
    )
    return obj


@pytest.fixture
def horizontal_adduction_movement():
    obj, _ = MovementPattern.objects.get_or_create(
        code=MovementPatternVocabulary.HORIZONTAL_ADDUCTION,
        defaults={"label": "Horizontal Adduction"},
    )
    return obj


@pytest.fixture
def anterior_direction():
    obj, _ = AnatomicalDirection.objects.get_or_create(
        code=AnatomicalDirectionVocabulary.ANTERIOR, defaults={"label": "Anterior"}
    )
    return obj


@pytest.fixture
def agonist_role():
    obj, _ = MuscleRole.objects.get_or_create(
        code=MuscleRoleVocabulary.AGONIST, defaults={"label": "Agonist"}
    )
    return obj


@pytest.fixture
def upper_arm_group():
    obj, _ = MuscleGroup.objects.get_or_create(
        code=MuscleGroupVocabulary.UPPER_ARM, defaults={"label": "Upper Arm"}
    )
    return obj


@pytest.fixture
def chest_group():
    obj, _ = MuscleGroup.objects.get_or_create(
        code=MuscleGroupVocabulary.CHEST, defaults={"label": "Chest"}
    )
    return obj


@pytest.fixture
def biceps_muscle(anterior_direction, upper_arm_group):
    obj, _ = Muscle.objects.get_or_create(
        code="BICEPS_BRACHII",
        defaults={
            "label": "Biceps Brachii",
            "anatomical_direction": anterior_direction,
            "muscle_group": upper_arm_group,
        },
    )
    return obj


@pytest.fixture
def pec_major_muscle(anterior_direction, chest_group):
    obj, _ = Muscle.objects.get_or_create(
        code="PECTORALIS_MAJOR",
        defaults={
            "label": "Pectoralis Major",
            "anatomical_direction": anterior_direction,
            "muscle_group": chest_group,
        },
    )
    return obj


@pytest.fixture
def elbow_flexion_joint_action(elbow_joint, flexion_movement, sagittal_plane):
    obj, _ = JointAction.objects.get_or_create(
        joint=elbow_joint,
        movement=flexion_movement,
        defaults={"plane": sagittal_plane},
    )
    return obj


@pytest.fixture
def horizontal_adduction_joint_action(
    shoulder_joint, horizontal_adduction_movement, transverse_plane
):
    obj, _ = JointAction.objects.get_or_create(
        joint=shoulder_joint,
        movement=horizontal_adduction_movement,
        defaults={"plane": transverse_plane},
    )
    return obj


@pytest.fixture
def bicep_elbow_flexion_involvement(
    biceps_muscle, elbow_flexion_joint_action, agonist_role
):
    obj, _ = MuscleInvolvement.objects.get_or_create(
        muscle=biceps_muscle,
        joint_action=elbow_flexion_joint_action,
        defaults={"role": agonist_role, "impact_factor": Decimal("0.80")},
    )
    return obj


@pytest.fixture
def pec_major_horizontal_adduction_involvement(
    pec_major_muscle, horizontal_adduction_joint_action, agonist_role
):
    obj, _ = MuscleInvolvement.objects.get_or_create(
        muscle=pec_major_muscle,
        joint_action=horizontal_adduction_joint_action,
        defaults={"role": agonist_role, "impact_factor": Decimal("0.80")},
    )
    return obj


# ── Exercise lookups ──────────────────────────────────────────────────────────


@pytest.fixture
def dumbbell_equipment():
    obj, _ = Equipment.objects.get_or_create(
        code="DUMBBELL", defaults={"label": "Dumbbell"}
    )
    return obj


@pytest.fixture
def barbell_equipment():
    obj, _ = Equipment.objects.get_or_create(
        code="BARBELL", defaults={"label": "Barbell"}
    )
    return obj


@pytest.fixture
def concentric_phase():
    obj, _ = ExercisePhase.objects.get_or_create(
        code=ExercisePhaseVocabulary.CONCENTRIC, defaults={"label": "Concentric"}
    )
    return obj


@pytest.fixture
def full_range_of_motion():
    obj, _ = JointRangeOfMotion.objects.get_or_create(
        code=JointRangeOfMotionVocabulary.FULL,
        defaults={"label": "Full", "impact_factor": Decimal("1.00")},
    )
    return obj


@pytest.fixture
def partial_range_of_motion():
    obj, _ = JointRangeOfMotion.objects.get_or_create(
        code=JointRangeOfMotionVocabulary.PARTIAL,
        defaults={"label": "Partial", "impact_factor": Decimal("0.50")},
    )
    return obj


# ── Exercise domain fixtures ──────────────────────────────────────────────────


@pytest.fixture
def dumbbell_bicep_curl_exercise(dumbbell_equipment, level_beginner):
    exercise, _ = Exercise.objects.get_or_create(
        exercise_name="Dumbbell Bicep Curl",
        defaults={
            "api_name": "dumbbell_bicep_curl",
            "instructions": "Curl the dumbbell upward.",
            "safety_tips": "Keep elbows tucked.",
            "experience_level": level_beginner,
        },
    )
    exercise.equipment.add(dumbbell_equipment)
    return exercise


@pytest.fixture
def barbell_bench_press_exercise(barbell_equipment, level_advanced):
    exercise, _ = Exercise.objects.get_or_create(
        exercise_name="Barbell Bench Press",
        defaults={
            "api_name": "barbell_bench_press",
            "instructions": "Press the bar upward.",
            "safety_tips": "Use a spotter.",
            "experience_level": level_advanced,
        },
    )
    exercise.equipment.add(barbell_equipment)
    return exercise


@pytest.fixture
def concentric_bicep_curl_movement(dumbbell_bicep_curl_exercise, concentric_phase):
    obj, _ = ExerciseMovement.objects.get_or_create(
        phase=concentric_phase, exercise=dumbbell_bicep_curl_exercise
    )
    return obj


@pytest.fixture
def concentric_bench_press_movement(barbell_bench_press_exercise, concentric_phase):
    obj, _ = ExerciseMovement.objects.get_or_create(
        phase=concentric_phase, exercise=barbell_bench_press_exercise
    )
    return obj


@pytest.fixture
def elbow_flexion_joint_contribution(
    elbow_flexion_joint_action, full_range_of_motion, concentric_bicep_curl_movement
):
    obj, _ = JointContribution.objects.get_or_create(
        joint_action=elbow_flexion_joint_action,
        exercise_movement=concentric_bicep_curl_movement,
        defaults={"joint_range_of_motion": full_range_of_motion},
    )
    return obj


@pytest.fixture
def horizontal_adduction_joint_contribution(
    horizontal_adduction_joint_action,
    full_range_of_motion,
    concentric_bench_press_movement,
):
    obj, _ = JointContribution.objects.get_or_create(
        joint_action=horizontal_adduction_joint_action,
        exercise_movement=concentric_bench_press_movement,
        defaults={"joint_range_of_motion": full_range_of_motion},
    )
    return obj


# ── Aliases — programs conftest uses beginner_level/advanced_level naming ────


@pytest.fixture
def beginner_level(level_beginner):
    return level_beginner


@pytest.fixture
def advanced_level(level_advanced):
    return level_advanced


# ── Biology fixture aliases ───────────────────────────────────────────────────
# Biology tests use bicep_muscle (no s), root conftest defines biceps_muscle.


@pytest.fixture
def bicep_muscle(biceps_muscle):
    return biceps_muscle


@pytest.fixture
def intermediate_level(level_intermediate):
    return level_intermediate
