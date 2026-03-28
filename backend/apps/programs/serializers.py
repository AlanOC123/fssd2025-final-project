from django.contrib.auth import get_user_model
from rest_framework import serializers

from apps.users.models import ExperienceLevel, TrainerClientMembership, TrainingGoal
from apps.users.serializers import (
    ExperienceLevelSerializer,
    TrainingGoalSerializer,
)
from core.serializers import (
    ApexSerializer,
    LabelLookupSerializer,
    NormalisedLookupSerializer,
)

from .models import (
    Program,
    ProgramPhase,
    ProgramPhaseOption,
    ProgramPhaseStatusOption,
    ProgramStatusOption,
)

User = get_user_model()


class ProgramPhaseOptionSerializer(LabelLookupSerializer):
    """Serializer for ProgramPhaseOption lookup data.

    Includes additional duration fields for planning defaults.
    """

    class Meta(LabelLookupSerializer.Meta):
        """Metadata options for ProgramPhaseOptionSerializer."""

        model = ProgramPhaseOption
        fields = LabelLookupSerializer.Meta.fields + [
            "default_duration_days",
            "default_duration_weeks",
        ]
        read_only_fields = fields


class ProgramStatusOptionSerializer(NormalisedLookupSerializer):
    """Serializer for ProgramStatusOption normalized lookups."""

    class Meta(LabelLookupSerializer.Meta):
        """Metadata options for ProgramStatusOptionSerializer."""

        model = ProgramStatusOption


class ProgramPhaseStatusOptionSerializer(NormalisedLookupSerializer):
    """Serializer for ProgramPhaseStatusOption normalized lookups."""

    class Meta(LabelLookupSerializer.Meta):
        """Metadata options for ProgramPhaseStatusOptionSerializer."""

        model = ProgramPhaseStatusOption


class ProgramPhaseWriteSerializer(ApexSerializer):
    """Serializer for handling creation and modification of ProgramPhase instances.

    Attributes:
        program_id: Primary key of the parent program.
        phase_option_id: Primary key of the template phase option.
    """

    program_id = serializers.PrimaryKeyRelatedField(
        queryset=Program.objects.all(),
        source="program",
        write_only=True,
    )

    phase_option_id = serializers.PrimaryKeyRelatedField(
        queryset=ProgramPhaseOption.objects.all(),
        source="phase_option",
        write_only=True,
    )

    class Meta(ApexSerializer.Meta):
        """Metadata options for ProgramPhaseWriteSerializer."""

        model = ProgramPhase
        fields = ApexSerializer.Meta.fields + [
            "program_id",
            "phase_option_id",
            "phase_name",
            "phase_goal",
            "sequence_order",
            "trainer_notes",
            "client_notes",
            "planned_start_date",
            "planned_end_date",
        ]

    def validate(self, attrs):
        """Validates that planned date ranges are logically consistent.

        Args:
            attrs: Dictionary of input data.

        Returns:
            The validated data dictionary.

        Raises:
            serializers.ValidationError: If planned_start_date is on or
                after planned_end_date.
        """
        planned_start_date = attrs.get("planned_start_date")
        planned_end_date = attrs.get("planned_end_date")

        if planned_start_date and planned_end_date:
            if planned_start_date >= planned_end_date:
                raise serializers.ValidationError(
                    "Planned start date must be before planned end date."
                )

        return attrs


class ProgramPhaseReadSerializer(ApexSerializer):
    """Serializer for detailed retrieval of ProgramPhase instances.

    Attributes:
        phase_option: Nested detail of the phase type.
        status: Nested detail of current phase status.
        duration_days: Calculated field for total days.
        duration_weeks: Calculated field for total weeks.
    """

    phase_option = ProgramPhaseOptionSerializer(read_only=True)
    status = ProgramPhaseStatusOptionSerializer(read_only=True)

    program_id = serializers.UUIDField(source="program.id", read_only=True)

    created_by_trainer_id = serializers.UUIDField(
        source="created_by_trainer.id",
        read_only=True,
        allow_null=True,
    )
    last_edited_by_id = serializers.UUIDField(
        source="last_edited_by.id",
        read_only=True,
        allow_null=True,
    )

    duration_days = serializers.IntegerField(read_only=True)
    duration_weeks = serializers.IntegerField(read_only=True)

    class Meta(ApexSerializer.Meta):
        """Metadata options for ProgramPhaseReadSerializer."""

        model = ProgramPhase
        fields = ApexSerializer.Meta.fields + [
            "program_id",
            "phase_option",
            "phase_name",
            "phase_goal",
            "sequence_order",
            "status",
            "trainer_notes",
            "client_notes",
            "planned_start_date",
            "planned_end_date",
            "actual_start_date",
            "actual_end_date",
            "started_at",
            "completed_at",
            "created_by_trainer_id",
            "last_edited_by_id",
            "skipped_at",
            "skipped_reason",
            "archived_at",
            "archived_reason",
            "duration_days",
            "duration_weeks",
        ]
        read_only_fields = fields


class ProgramPhaseListSerializer(ApexSerializer):
    """Simplified serializer for listing ProgramPhases within program summaries."""

    phase_option = ProgramPhaseOptionSerializer(read_only=True)
    status = ProgramPhaseStatusOptionSerializer(read_only=True)

    duration_days = serializers.IntegerField(read_only=True)
    duration_weeks = serializers.IntegerField(read_only=True)

    class Meta(ApexSerializer.Meta):
        """Metadata options for ProgramPhaseListSerializer."""

        model = ProgramPhase
        fields = ApexSerializer.Meta.fields + [
            "phase_option",
            "phase_name",
            "phase_goal",
            "sequence_order",
            "status",
            "planned_start_date",
            "planned_end_date",
            "actual_start_date",
            "actual_end_date",
            "duration_days",
            "duration_weeks",
        ]
        read_only_fields = fields


class ProgramPhaseReasonSerializer(serializers.Serializer):
    """Serializer for endpoints requiring a mandatory reason (skip/archive)."""

    reason = serializers.CharField(
        max_length=200,
        required=True,
        allow_blank=False,
        trim_whitespace=True,
    )


class ProgramWriteSerializer(ApexSerializer):
    """Serializer for handling creation and modification of Program instances."""

    trainer_client_membership_id = serializers.PrimaryKeyRelatedField(
        queryset=TrainerClientMembership.objects.all(),
        source="trainer_client_membership",
        write_only=True,
    )

    experience_level_id = serializers.PrimaryKeyRelatedField(
        queryset=ExperienceLevel.objects.all(),
        source="experience_level",
        write_only=True,
    )

    training_goal_id = serializers.PrimaryKeyRelatedField(
        queryset=TrainingGoal.objects.all(),
        source="training_goal",
        write_only=True,
    )

    class Meta(ApexSerializer.Meta):
        """Metadata options for ProgramWriteSerializer."""

        model = Program
        fields = ApexSerializer.Meta.fields + [
            "program_name",
            "trainer_client_membership_id",
            "experience_level_id",
            "training_goal_id",
        ]


class ProgramListSerializer(ApexSerializer):
    """Serializer for listing programs with high-level summaries and durations."""

    trainer_client_membership_id = serializers.UUIDField(
        source="trainer_client_membership.id",
        read_only=True,
    )
    experience_level = ExperienceLevelSerializer(read_only=True)
    training_goal = TrainingGoalSerializer(read_only=True)
    status = ProgramStatusOptionSerializer(read_only=True)

    planned_start_date = serializers.DateField(read_only=True)
    planned_end_date = serializers.DateField(read_only=True)
    actual_start_date = serializers.DateField(read_only=True)
    actual_end_date = serializers.DateField(read_only=True)

    program_duration_days = serializers.IntegerField(read_only=True)
    program_duration_weeks = serializers.IntegerField(read_only=True)
    has_created_phases = serializers.BooleanField(read_only=True)
    number_of_completed_phases = serializers.IntegerField(read_only=True)
    number_of_skipped_phases = serializers.IntegerField(read_only=True)
    number_of_archived_phases = serializers.IntegerField(read_only=True)
    remaining_phases = ProgramPhaseListSerializer(many=True, read_only=True)
    all_phases_finished = serializers.BooleanField(read_only=True)

    class Meta(ApexSerializer.Meta):
        """Metadata options for ProgramListSerializer."""

        model = Program
        fields = ApexSerializer.Meta.fields + [
            "program_name",
            "version",
            "trainer_client_membership_id",
            "experience_level",
            "training_goal",
            "status",
            "planned_start_date",
            "planned_end_date",
            "actual_start_date",
            "actual_end_date",
            "program_duration_days",
            "program_duration_weeks",
            "has_created_phases",
            "number_of_completed_phases",
            "number_of_skipped_phases",
            "number_of_archived_phases",
            "remaining_phases",
            "all_phases_finished",
            "submitted_for_review_at",
            "reviewed_at",
            "started_at",
            "completed_at",
            "abandoned_at",
        ]
        read_only_fields = fields


class ProgramDetailSerializer(ApexSerializer):
    """Full detail serializer for Program instances including all phases.

    Includes deep nested details for phases and audit-trail fields.
    """

    trainer_client_membership_id = serializers.UUIDField(
        source="trainer_client_membership.id",
        read_only=True,
    )
    experience_level = ExperienceLevelSerializer(read_only=True)
    training_goal = TrainingGoalSerializer(read_only=True)
    status = ProgramStatusOptionSerializer(read_only=True)

    created_by_trainer_id = serializers.UUIDField(
        source="created_by_trainer.id",
        read_only=True,
        allow_null=True,
    )
    last_edited_by_id = serializers.UUIDField(
        source="last_edited_by.id",
        read_only=True,
        allow_null=True,
    )

    planned_start_date = serializers.DateField(read_only=True)
    planned_end_date = serializers.DateField(read_only=True)
    actual_start_date = serializers.DateField(read_only=True)
    actual_end_date = serializers.DateField(read_only=True)

    program_duration_days = serializers.IntegerField(read_only=True)
    program_duration_weeks = serializers.IntegerField(read_only=True)
    has_created_phases = serializers.BooleanField(read_only=True)
    number_of_completed_phases = serializers.IntegerField(read_only=True)
    number_of_skipped_phases = serializers.IntegerField(read_only=True)
    number_of_archived_phases = serializers.IntegerField(read_only=True)
    all_phases_finished = serializers.BooleanField(read_only=True)

    phases = ProgramPhaseReadSerializer(many=True, read_only=True)

    class Meta(ApexSerializer.Meta):
        """Metadata options for ProgramDetailSerializer."""

        model = Program
        fields = ApexSerializer.Meta.fields + [
            "program_name",
            "version",
            "trainer_client_membership_id",
            "experience_level",
            "training_goal",
            "status",
            "created_by_trainer_id",
            "last_edited_by_id",
            "submitted_for_review_at",
            "reviewed_at",
            "started_at",
            "completed_at",
            "abandoned_at",
            "review_notes",
            "completion_notes",
            "abandonment_reason",
            "planned_start_date",
            "planned_end_date",
            "actual_start_date",
            "actual_end_date",
            "program_duration_days",
            "program_duration_weeks",
            "has_created_phases",
            "number_of_completed_phases",
            "number_of_skipped_phases",
            "number_of_archived_phases",
            "all_phases_finished",
            "phases",
        ]
        read_only_fields = fields


class ProgramReviewSerializer(serializers.Serializer):
    """Serializer for processing program review outcomes."""

    feedback_notes = serializers.CharField(
        max_length=500,
        required=False,
        allow_blank=True,
        trim_whitespace=True,
    )
    is_accepted = serializers.BooleanField(required=True)


class ProgramCompleteSerializer(serializers.Serializer):
    """Serializer for finalizing a completed program."""

    completion_notes = serializers.CharField(
        max_length=500,
        required=True,
        allow_blank=False,
        trim_whitespace=True,
    )


class ProgramAbandonSerializer(serializers.Serializer):
    """Serializer for recording the abandonment of a program."""

    abandonment_reason = serializers.CharField(
        max_length=200,
        required=True,
        allow_blank=False,
        trim_whitespace=True,
    )
