from rest_framework import serializers

from apps.biology.serializers import JointActionSerializer
from apps.users.serializers import ExperienceLevelSerializer

from .models import (
    Equipment,
    Exercise,
    ExerciseMovement,
    ExercisePhase,
    JointContribution,
    JointRangeOfMotion,
)


class JointRangeOfMotionSerializer(serializers.ModelSerializer):
    class Meta:
        model = JointRangeOfMotion
        fields = ["id", "range_of_motion_name", "impact_factor"]


class ExercisePhaseSerializer(serializers.ModelSerializer):
    class Meta:
        model = ExercisePhase
        fields = ["id", "phase_name"]


class EquipmentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Equipment
        fields = ["id", "equipment_name"]


class ExerciseSerializer(serializers.ModelSerializer):
    experience_level = ExperienceLevelSerializer(read_only=True)
    equipment = EquipmentSerializer(read_only=True, many=True)

    class Meta:
        model = Exercise
        fields = [
            "id",
            "exercise_name",
            "api_name",
            "equipment",
            "experience_level",
            "instructions",
            "safety_tips",
            "is_enriched",
        ]


class ExerciseMovementSerializer(serializers.ModelSerializer):
    phase = ExercisePhaseSerializer(read_only=True)
    exercise = ExerciseSerializer(read_only=True)

    class Meta:
        model = ExerciseMovement
        fields = ["id", "phase", "exercise"]


class JointContributionSerializer(serializers.ModelSerializer):
    joint_action = JointActionSerializer(read_only=True)
    joint_range_of_motion = JointRangeOfMotionSerializer(read_only=True)
    exercise_movement = ExerciseMovementSerializer(read_only=True)

    class Meta:
        model = JointContribution
        fields = ["id", "joint_action", "joint_range_of_motion", "exercise_movement"]
