from rest_framework import serializers

from apps.users.serializers import (
    ExperienceLevelSerializer,
    TrainerClientMembershipSerializer,
    TrainingGoalSerializer,
)

from apps.users.models import TrainingGoal, ExperienceLevel, TrainerClientMembership

from .models import Program, ProgramPhase, ProgramPhaseOption


class ProgramPhaseOptionSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProgramPhaseOption
        fields = ["id", "phase_name", "order_index", "default_duration", "description"]


class ProgramPhaseSerializer(serializers.ModelSerializer):
    program_id = serializers.PrimaryKeyRelatedField(
        queryset=Program.objects.all(), source="program", write_only=True
    )

    phase_option = ProgramPhaseOptionSerializer(read_only=True)
    phase_option_id = serializers.PrimaryKeyRelatedField(
        queryset=ProgramPhaseOption.objects.all(),
        source="phase_option",
        write_only=True,
    )

    class Meta:
        model = ProgramPhase
        fields = [
            "id",
            "is_active",
            "is_completed",
            "completed_at",
            "custom_duration",
            "phase_option",
            "phase_option_id",
            "program_id",
        ]


class ProgramSerializer(serializers.ModelSerializer):
    training_goal = TrainingGoalSerializer(read_only=True)
    training_goal_id = serializers.PrimaryKeyRelatedField(
        queryset=TrainingGoal.objects.all(), source="training_goal", write_only=True
    )

    experience_level = ExperienceLevelSerializer(read_only=True)
    experience_level_id = serializers.PrimaryKeyRelatedField(
        queryset=ExperienceLevel.objects.all(),
        source="experience_level",
        write_only=True,
    )

    trainer_client_membership_id = serializers.PrimaryKeyRelatedField(
        queryset=TrainerClientMembership.objects.all(),
        source="trainer_client_membership",
    )

    phases = ProgramPhaseSerializer(many=True, read_only=True)
    calculated_duration = serializers.IntegerField(read_only=True)

    class Meta:
        model = Program
        fields = [
            "id",
            "program_name",
            "training_goal",
            "training_goal_id",
            "experience_level",
            "experience_level_id",
            "phases",
            "calculated_duration",
            "trainer_client_membership_id",
        ]
