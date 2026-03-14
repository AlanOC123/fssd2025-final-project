from dj_rest_auth.registration.serializers import RegisterSerializer
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
    """Used for matching trainers with clients"""

    first_name = serializers.CharField(source="user.first_name", read_only=True)
    last_name = serializers.CharField(source="user.last_name", read_only=True)
    email = serializers.CharField(source="user.email", read_only=True)

    specialisations = TrainingGoalSerializer(many=True, read_only=True)
    accepted_experience_levels = ExperienceLevelSerializer(many=True, read_only=True)

    class Meta:
        model = TrainerProfile
        fields = [
            "id",
            "first_name",
            "last_name",
            "email",
            "specialisations",
            "accepted_experience_levels",
            "company",
            "website",
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


class CustomRegisterSerializer(RegisterSerializer):
    username = None

    def get_cleaned_data(self):
        data = super().get_cleaned_data()

        if "username" in data:
            del data["username"]

        return data


class TrainerClientMembershipSerializer(serializers.ModelSerializer):
    trainer_name = serializers.CharField(
        source="trainer.user.get_full_name", read_only=True
    )
    client_name = serializers.CharField(
        source="client.user.get_full_name", read_only=True
    )
    status_name = serializers.CharField(source="status.status_name", read_only=True)

    trainer_id = serializers.PrimaryKeyRelatedField(
        queryset=TrainerProfile.objects.all(),
        source="trainer",
        required=False,
    )

    status_id = serializers.PrimaryKeyRelatedField(
        queryset=MembershipStatus.objects.all(),
        source="status",
        required=False,
    )

    class Meta:
        model = TrainerClientMembership

        fields = [
            "id",
            "trainer_name",
            "client_name",
            "status_name",
            "trainer_id",
            "status_id",
            "created_at",
            "updated_at",
        ]

        read_only_fields = ["created_at", "updated_at"]

    def validate(self, attrs):
        if self.instance is None:
            user = self.context["request"].user

            if user.is_client:
                has_active = TrainerClientMembership.objects.filter(
                    client=user.client_profile,
                    status__status_name__in=["ACTIVE", "PENDING_TRAINER_REVIEW"],
                ).exists()

                if has_active:
                    raise serializers.ValidationError(
                        "You already have an active or pending trainer request."
                    )

        return attrs
