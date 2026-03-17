from dj_rest_auth.registration.serializers import RegisterSerializer
from django.contrib.auth import get_user_model
from rest_framework import serializers

from core.serializers import ApexSerializer, LabelLookupSerializer

from .models import (
    ClientProfile,
    ExperienceLevel,
    TrainerClientMembership,
    TrainerProfile,
    TrainingGoal,
)

User = get_user_model()


class UserIdSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ["id"]
        read_only_fields = fields


class TrainingGoalSerializer(LabelLookupSerializer):

    class Meta(LabelLookupSerializer.Meta):
        model = TrainingGoal


class ExperienceLevelSerializer(LabelLookupSerializer):
    class Meta(LabelLookupSerializer.Meta):
        model = ExperienceLevel


class ClientProfileSerializer(ApexSerializer):
    goal = TrainingGoalSerializer(read_only=True)
    level = ExperienceLevelSerializer(read_only=True)

    goal_id = serializers.PrimaryKeyRelatedField(
        queryset=TrainingGoal.objects.all(),
        source="goal",
        write_only=True,
        required=False,
        allow_null=True,
    )

    level_id = serializers.PrimaryKeyRelatedField(
        queryset=ExperienceLevel.objects.all(),
        source="level",
        write_only=True,
        required=False,
        allow_null=True,
    )

    class Meta(ApexSerializer.Meta):
        model = ClientProfile
        fields = ApexSerializer.Meta.fields + [
            "goal",
            "level",
            "goal_id",
            "level_id",
            "avatar",
        ]
        read_only_fields = ApexSerializer.Meta.read_only_fields + ["goal", "level"]


class TrainerProfileSerializer(ApexSerializer):
    """Used for matching trainers with clients"""

    accepted_goals = TrainingGoalSerializer(many=True, read_only=True)
    accepted_levels = ExperienceLevelSerializer(many=True, read_only=True)

    accepted_goal_ids = serializers.PrimaryKeyRelatedField(
        queryset=TrainingGoal.objects.all(),
        source="accepted_goals",
        write_only=True,
        required=False,
        many=True,
    )

    accepted_level_ids = serializers.PrimaryKeyRelatedField(
        queryset=ExperienceLevel.objects.all(),
        source="accepted_levels",
        write_only=True,
        required=False,
        many=True,
    )

    class Meta(ApexSerializer.Meta):
        model = TrainerProfile
        fields = ApexSerializer.Meta.fields + [
            "accepted_goals",
            "accepted_levels",
            "accepted_goal_ids",
            "accepted_level_ids",
            "company",
            "website",
            "logo",
        ]

        read_only_fields = ApexSerializer.Meta.read_only_fields + [
            "accepted_goals",
            "accepted_levels",
        ]


class TrainerMatchingSerializer(ApexSerializer):
    first_name = serializers.CharField(source="user.first_name", read_only=True)
    last_name = serializers.CharField(source="user.last_name", read_only=True)
    email = serializers.CharField(source="user.email", read_only=True)

    accepted_goals = TrainingGoalSerializer(many=True, read_only=True)
    accepted_levels = ExperienceLevelSerializer(many=True, read_only=True)

    class Meta(ApexSerializer.Meta):
        model = TrainerProfile
        fields = ApexSerializer.Meta.fields + [
            "first_name",
            "last_name",
            "email",
            "accepted_goals",
            "accepted_levels",
        ]

        read_only_fields = ApexSerializer.Meta.fields + fields


class CustomUserSerializer(ApexSerializer):
    profile = serializers.SerializerMethodField()
    role = serializers.SerializerMethodField()
    full_name = serializers.SerializerMethodField()

    class Meta(ApexSerializer.Meta):
        model = User
        fields = ApexSerializer.Meta.fields + [
            "email",
            "first_name",
            "last_name",
            "full_name",
            "is_trainer",
            "is_client",
            "role",
            "profile",
        ]

    def get_full_name(self, obj):
        return obj.get_full_name()

    def get_role(self, obj):
        if obj.is_superuser:
            return "admin"
        if obj.is_trainer:
            return "trainer"
        if obj.is_client:
            return "client"
        return "unknown"

    def get_profile(self, obj):
        if obj.is_client and hasattr(obj, "client_profile"):
            return ClientProfileSerializer(obj.client_profile).data

        if obj.is_trainer and hasattr(obj, "trainer_profile"):
            return TrainerProfileSerializer(obj.trainer_profile).data

        return None


class CustomRegisterSerializer(RegisterSerializer):
    username = None

    def get_cleaned_data(self):
        data = super().get_cleaned_data()

        if "username" in data:
            data.pop("username", None)

        return data


class TrainerClientMembershipSerializer(ApexSerializer):
    trainer_name = serializers.SerializerMethodField()
    client_name = serializers.SerializerMethodField()

    status_code = serializers.CharField(source="status.code", read_only=True)
    status_label = serializers.CharField(source="status.label", read_only=True)

    trainer_id = serializers.PrimaryKeyRelatedField(
        queryset=TrainerProfile.objects.all(),
        source="trainer",
        required=False,
        write_only=True,
    )

    status_id = serializers.UUIDField(source="status.id", read_only=True)

    class Meta(ApexSerializer.Meta):
        model = TrainerClientMembership

        fields = ApexSerializer.Meta.fields + [
            "trainer_name",
            "client_name",
            "status_code",
            "status_label",
            "status_id",
            "trainer_id",
            "requested_at",
            "responded_at",
            "started_at",
            "ended_at",
        ]

        read_only_fields = ApexSerializer.Meta.read_only_fields + [
            "trainer_name",
            "client_name",
            "status_id",
            "status_code",
            "status_label",
            "requested_at",
            "responded_at",
            "started_at",
            "ended_at",
        ]

    def get_trainer_name(self, obj):
        name = obj.trainer.user.get_full_name()
        return name if name else obj.trainer.user.email

    def get_client_name(self, obj):
        name = obj.client.user.get_full_name()
        return name if name else obj.client.user.email


class MembershipRequestSerializer(serializers.Serializer):
    trainer_id = serializers.PrimaryKeyRelatedField(
        queryset=TrainerProfile.objects.all(),
    )
