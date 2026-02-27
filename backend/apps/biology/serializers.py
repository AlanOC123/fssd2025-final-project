from rest_framework import serializers

from .models import (
    AnatomicalDirection,
    Joint,
    JointAction,
    MovementPattern,
    Muscle,
    MuscleInvolvement,
    MuscleRole,
    PlaneOfMotion,
)


class PlaneOfMotionSerializer(serializers.ModelSerializer):
    class Meta:
        model = PlaneOfMotion
        fields = ["id", "plane_name"]


class AnatomicalDirectionSerializer(serializers.ModelSerializer):
    class Meta:
        model = AnatomicalDirection
        fields = ["id", "direction_name"]


class MovementPatternSerializer(serializers.ModelSerializer):
    class Meta:
        model = MovementPattern
        fields = ["id", "pattern_name"]


class MuscleRoleSerializer(serializers.ModelSerializer):
    class Meta:
        model = MuscleRole
        fields = ["id", "role_name"]


class JointSerializer(serializers.ModelSerializer):
    class Meta:
        model = Joint
        fields = ["id", "joint_name"]


class JointActionSerializer(serializers.ModelSerializer):
    joint = JointSerializer(read_only=True)
    movement = MovementPatternSerializer(read_only=True)
    plane = PlaneOfMotionSerializer(read_only=True)

    class Meta:
        model = JointAction
        fields = ["id", "joint", "movement", "plane"]


class MuscleSerializer(serializers.ModelSerializer):
    anatomical_direction = AnatomicalDirectionSerializer(read_only=True)

    class Meta:
        model = Muscle
        fields = ["id", "muscle_name", "anatomical_direction"]


class MuscleInvolvementSerializer(serializers.ModelSerializer):
    muscle = MuscleSerializer(read_only=True)

    joint_action = JointActionSerializer(read_only=True)

    role = MuscleRoleSerializer(read_only=True)

    class Meta:
        model = MuscleInvolvement
        fields = ["id", "joint_action", "role", "impact_factor", "muscle"]
