from rest_framework import serializers

from apps.users.serializers import (
    ExperienceLevelSerializer,
    TrainerClientMembershipSerializer,
    TrainingGoalSerializer,
)

from .models import Program, ProgramPhase, ProgramPhaseOption


class ProgramPhaseOptionSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProgramPhaseOption
        fields = ["id", "phase_name", "order_index", "default_duration", "description"]


class ProgramPhaseSerializer(serializers.ModelSerializer):
    phase_option = ProgramPhaseOptionSerializer(read_only=True)

    class Meta:
        model = ProgramPhase
        fields = [
            "id",
            "is_active",
            "is_completed",
            "completed_at",
            "custom_duration",
            "phase_option",
        ]


class ProgramSerializer(serializers.ModelSerializer):
    trainer_goal = TrainingGoalSerializer(read_only=True)
    experience_level = ExperienceLevelSerializer(read_only=True)

    phases = ProgramPhaseSerializer(many=True, read_only=True)

    trainer_client_membership = TrainerClientMembershipSerializer(read_only=True)

    calculated_duration = serializers.IntegerField(read_only=True)

    class Meta:
        model = Program
        fields = [
            "id",
            "program_name",
            "trainer_goal",
            "experience_level",
            "phases",
            "calculated_duration",
            "trainer_client_membership",
        ]
