from django.contrib.auth import get_user_model
from rest_framework import serializers

from .models import (
    ClientProfile,
    ExperienceLevel,
    MembershipStatus,
    TrainerClientMembership,
    TrainerProfile,
    TrainingGoal,
)

User = get_user_model()


class TrainingGoalSerializer(serializers.ModelSerializer):
    class Meta:
        model = TrainingGoal
        fields = ["id", "goal_name"]


class ExperienceLevelSerializer(serializers.ModelSerializer):
    class Meta:
        model = ExperienceLevel
        fields = ["id", "level_name"]


class MembershipStatusSerializer(serializers.ModelSerializer):
    class Meta:
        model = MembershipStatus
        fields = ["id", "status_name"]


class ClientProfileSerializer(serializers.ModelSerializer):
    training_goal = TrainingGoalSerializer(read_only=True)
    experience_level = ExperienceLevelSerializer(read_only=True)

    class Meta:
        model = ClientProfile
        fields = ["id", "training_goal", "experience_level"]


class TrainerProfileSerializer(serializers.ModelSerializer):
    specialisations = TrainingGoalSerializer(many=True, read_only=True)
    accepted_experience_levels = ExperienceLevelSerializer(many=True, read_only=True)

    class Meta:
        model = TrainerProfile
        fields = [
            "id",
            "specialisations",
            "accepted_experience_levels",
        ]


class CustomUserSerializer(serializers.ModelSerializer):
    profile = serializers.SerializerMethodField()
    role = serializers.SerializerMethodField()
    full_name = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = [
            "id",
            "email",
            "first_name",
            "last_name",
            "full_name",
            "is_trainer",
            "is_client",
            "role",
            "profile",
        ]

        read_only_fields = ["id"]

    def get_full_name(self, obj):
        return f"{obj.first_name} {obj.last_name}"

    def get_role(self, obj):
        if obj.is_trainer:
            return "trainer"
        if obj.is_client:
            return "client"
        if obj.is_superuser:
            return "admin"

        return "unknown"

    def get_profile(self, obj):
        if obj.is_client and hasattr(obj, "client_profile"):
            return ClientProfileSerializer(obj.client_profile).data

        elif obj.is_trainer and hasattr(obj, "trainer_profile"):
            return TrainerProfileSerializer(obj.trainer_profile).data

        else:
            return None


class TrainerClientMembershipSerializer(serializers.ModelSerializer):
    trainer = TrainerProfileSerializer(read_only=True)
    client = ClientProfileSerializer(read_only=True)
    status = MembershipStatusSerializer(read_only=True)

    class Meta:
        model = TrainerClientMembership
        fields = ["id", "trainer", "status", "client"]
