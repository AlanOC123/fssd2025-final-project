from decimal import Decimal

from django.contrib.auth import get_user_model
from rest_framework import serializers

from apps.exercises.models import Exercise
from apps.exercises.serializers import ExerciseSerializer
from apps.programs.models import ProgramPhase
from core.serializers import ApexSerializer

from .models import (
    Workout,
    WorkoutCompletionRecord,
    WorkoutExercise,
    WorkoutExerciseCompletionRecord,
    WorkoutSet,
    WorkoutSetCompletionRecord,
)

User = get_user_model()


# Prescriptive: Write serializers (trainer)


class WorkoutWriteSerializer(ApexSerializer):
    """Serializer for trainers to create or update Workout instances.

    Attributes:
        program_phase_id: Write-only primary key for the associated ProgramPhase.
    """

    program_phase_id = serializers.PrimaryKeyRelatedField(
        queryset=ProgramPhase.objects.all(),
        source="program_phase",
        write_only=True,
    )

    class Meta(ApexSerializer.Meta):
        model = Workout
        fields = ApexSerializer.Meta.fields + [
            "program_phase_id",
            "workout_name",
            "planned_date",
        ]


class WorkoutExerciseWriteSerializer(ApexSerializer):
    """Serializer for trainers to create or update WorkoutExercise instances.

    Attributes:
        workout_id: Write-only primary key for the parent Workout.
        exercise_id: Write-only primary key for the associated Exercise.
    """

    workout_id = serializers.PrimaryKeyRelatedField(
        queryset=Workout.objects.all(),
        source="workout",
        write_only=True,
    )
    exercise_id = serializers.PrimaryKeyRelatedField(
        queryset=Exercise.objects.all(),
        source="exercise",
        write_only=True,
    )

    class Meta(ApexSerializer.Meta):
        model = WorkoutExercise
        fields = ApexSerializer.Meta.fields + [
            "workout_id",
            "exercise_id",
            "order",
            "sets_prescribed",
            "trainer_notes",
        ]


class WorkoutSetWriteSerializer(ApexSerializer):
    """Serializer for trainers to create or update WorkoutSet instances.

    Attributes:
        workout_exercise_id: Write-only primary key for the parent WorkoutExercise.
    """

    workout_exercise_id = serializers.PrimaryKeyRelatedField(
        queryset=WorkoutExercise.objects.all(),
        source="workout_exercise",
        write_only=True,
    )

    class Meta(ApexSerializer.Meta):
        model = WorkoutSet
        fields = ApexSerializer.Meta.fields + [
            "workout_exercise_id",
            "set_order",
            "reps_prescribed",
            "weight_prescribed",
        ]

    def validate_weight_prescribed(self, value):
        """Validates that the prescribed weight is non-negative.

        Args:
            value: The weight value to validate.

        Returns:
            Decimal: The validated weight.

        Raises:
            serializers.ValidationError: If weight is less than zero.
        """
        if value < Decimal("0.00"):
            raise serializers.ValidationError("weight_prescribed cannot be negative.")
        return value


# Prescriptive: Read serializers


class WorkoutSetReadSerializer(ApexSerializer):
    """Read-only serializer for WorkoutSet instances."""

    class Meta(ApexSerializer.Meta):
        model = WorkoutSet
        fields = ApexSerializer.Meta.fields + [
            "set_order",
            "reps_prescribed",
            "weight_prescribed",
        ]
        read_only_fields = fields


class WorkoutExerciseReadSerializer(ApexSerializer):
    """Read-only serializer for WorkoutExercise including nested targets.

    Attributes:
        exercise: Serialized summary of the exercise definition.
        sets: Nested list of prescribed sets.
    """

    exercise = ExerciseSerializer(read_only=True)
    sets = WorkoutSetReadSerializer(many=True, read_only=True)

    class Meta(ApexSerializer.Meta):
        model = WorkoutExercise
        fields = ApexSerializer.Meta.fields + [
            "order",
            "sets_prescribed",
            "trainer_notes",
            "exercise",
            "sets",
        ]
        read_only_fields = fields


class WorkoutReadSerializer(ApexSerializer):
    """Full read-only representation of a Workout with its exercise tree.

    Attributes:
        program_phase_id: UUID of the parent program phase.
        exercises: Nested list of exercise slots.
        has_session: Boolean indicating if a completion record exists.
    """

    program_phase_id = serializers.UUIDField(
        source="program_phase.id",
        read_only=True,
    )
    exercises = WorkoutExerciseReadSerializer(many=True, read_only=True)
    has_session = serializers.SerializerMethodField()

    class Meta(ApexSerializer.Meta):
        model = Workout
        fields = ApexSerializer.Meta.fields + [
            "workout_name",
            "planned_date",
            "program_phase_id",
            "exercises",
            "has_session",
        ]
        read_only_fields = fields

    def get_has_session(self, obj):
        """Checks for the existence of a completion record for the workout.

        Args:
            obj: The Workout instance.

        Returns:
            bool: True if a session record exists.
        """
        return WorkoutCompletionRecord.objects.filter(workout=obj).exists()


class WorkoutListSerializer(ApexSerializer):
    """Lightweight list view serializer for Workouts.

    Used for index views where nested exercise data is not required.
    """

    has_session = serializers.SerializerMethodField()

    program_phase_id = serializers.UUIDField(
        source="program_phase.id",
        read_only=True,
    )

    class Meta(ApexSerializer.Meta):
        model = Workout
        fields = ApexSerializer.Meta.fields + [
            "workout_name",
            "planned_date",
            "program_phase_id",
            "has_session",
        ]
        read_only_fields = fields

    def get_has_session(self, obj):
        """Checks for the existence of a completion record for the workout.

        Args:
            obj: The Workout instance.

        Returns:
            bool: True if a session record exists.
        """
        return WorkoutCompletionRecord.objects.filter(workout=obj).exists()


# Completion: Write serializers (client)


class StartWorkoutSerializer(serializers.Serializer):
    """Data transfer object for a client starting a workout session."""

    workout_id = serializers.PrimaryKeyRelatedField(
        queryset=Workout.objects.all(),
        source="workout",
    )


class StartExerciseSerializer(serializers.Serializer):
    """Data transfer object for a client starting a specific exercise."""

    workout_exercise_id = serializers.PrimaryKeyRelatedField(
        queryset=WorkoutExercise.objects.all(),
        source="workout_exercise",
    )
    session_id = serializers.PrimaryKeyRelatedField(
        queryset=WorkoutCompletionRecord.objects.all(),
        source="session",
    )


class CompleteSetSerializer(serializers.Serializer):
    """Data transfer object for recording set performance."""

    workout_set_id = serializers.PrimaryKeyRelatedField(
        queryset=WorkoutSet.objects.all(),
        source="workout_set",
    )
    exercise_record_id = serializers.PrimaryKeyRelatedField(
        queryset=WorkoutExerciseCompletionRecord.objects.all(),
        source="exercise_record",
    )
    reps_completed = serializers.IntegerField(min_value=1)
    weight_completed = serializers.DecimalField(
        max_digits=6,
        decimal_places=2,
        min_value=Decimal("0.00"),
    )
    difficulty_rating = serializers.IntegerField(
        min_value=1,
        max_value=10,
        required=False,
        allow_null=True,
    )
    reps_in_reserve = serializers.IntegerField(
        min_value=0,
        required=False,
        allow_null=True,
    )


class SkipSetSerializer(serializers.Serializer):
    """Data transfer object for recording a skipped set."""

    workout_set_id = serializers.PrimaryKeyRelatedField(
        queryset=WorkoutSet.objects.all(),
        source="workout_set",
    )
    exercise_record_id = serializers.PrimaryKeyRelatedField(
        queryset=WorkoutExerciseCompletionRecord.objects.all(),
        source="exercise_record",
    )


# Completion: Read serializers


class WorkoutSetCompletionReadSerializer(ApexSerializer):
    """Read-only serializer for set performance records.

    Attributes:
        workout_set_id: UUID of the original prescription.
        reps_diff: Difference between actual and prescribed reps.
        weight_diff: Difference between actual and prescribed weight.
    """

    workout_set_id = serializers.UUIDField(
        source="workout_set.id",
        read_only=True,
    )
    reps_diff = serializers.IntegerField(read_only=True)
    weight_diff = serializers.DecimalField(
        max_digits=6,
        decimal_places=2,
        read_only=True,
        allow_null=True,
    )

    class Meta(ApexSerializer.Meta):
        model = WorkoutSetCompletionRecord
        fields = ApexSerializer.Meta.fields + [
            "workout_set_id",
            "is_skipped",
            "completed_at",
            "reps_completed",
            "weight_completed",
            "difficulty_rating",
            "reps_in_reserve",
            "reps_diff",
            "weight_diff",
        ]
        read_only_fields = fields


class WorkoutExerciseCompletionReadSerializer(ApexSerializer):
    """Read-only serializer for exercise performance records.

    Attributes:
        workout_exercise_id: UUID of the original prescription.
        set_records: Nested list of set performance data.
    """

    workout_exercise_id = serializers.UUIDField(
        source="workout_exercise.id",
        read_only=True,
    )
    set_records = WorkoutSetCompletionReadSerializer(many=True, read_only=True)

    class Meta(ApexSerializer.Meta):
        model = WorkoutExerciseCompletionRecord
        fields = ApexSerializer.Meta.fields + [
            "workout_exercise_id",
            "is_skipped",
            "started_at",
            "completed_at",
            "set_records",
        ]
        read_only_fields = fields


class WorkoutCompletionReadSerializer(ApexSerializer):
    """Read-only serializer for full workout session records.

    Attributes:
        workout_id: UUID of the prescribed workout.
        client_id: UUID of the user.
        exercise_records: Nested list of exercise performance data.
        duration_s: Calculated session duration in seconds.
    """

    workout_id = serializers.UUIDField(
        source="workout.id",
        read_only=True,
    )
    client_id = serializers.UUIDField(
        source="client.id",
        read_only=True,
    )
    exercise_records = WorkoutExerciseCompletionReadSerializer(
        many=True,
        read_only=True,
    )
    duration_s = serializers.IntegerField(read_only=True, allow_null=True)

    class Meta(ApexSerializer.Meta):
        model = WorkoutCompletionRecord
        fields = ApexSerializer.Meta.fields + [
            "workout_id",
            "client_id",
            "is_skipped",
            "started_at",
            "completed_at",
            "duration_s",
            "exercise_records",
        ]
        read_only_fields = fields
