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


# Prescriptive: Write serializers (trainer) ─


class WorkoutWriteSerializer(ApexSerializer):
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
        if value < Decimal("0.00"):
            raise serializers.ValidationError("weight_prescribed cannot be negative.")
        return value


# Prescriptive: Read serializers


class WorkoutSetReadSerializer(ApexSerializer):
    class Meta(ApexSerializer.Meta):
        model = WorkoutSet
        fields = ApexSerializer.Meta.fields + [
            "set_order",
            "reps_prescribed",
            "weight_prescribed",
        ]
        read_only_fields = fields


class WorkoutExerciseReadSerializer(ApexSerializer):
    # Lean exercise summary — client doesn't need instructions mid-session
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
    program_phase_id = serializers.UUIDField(
        source="program_phase.id",
        read_only=True,
    )
    exercises = WorkoutExerciseReadSerializer(many=True, read_only=True)

    class Meta(ApexSerializer.Meta):
        model = Workout
        fields = ApexSerializer.Meta.fields + [
            "workout_name",
            "planned_date",
            "program_phase_id",
            "exercises",
        ]
        read_only_fields = fields


class WorkoutListSerializer(ApexSerializer):
    """
    Lightweight list view — no nested exercises.
    Client uses this to pick a workout; WorkoutReadSerializer
    is fetched on detail to get the full exercise/set tree.
    """

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
        ]
        read_only_fields = fields


# Completion: Write serializers (client) ─


class StartWorkoutSerializer(serializers.Serializer):
    workout_id = serializers.PrimaryKeyRelatedField(
        queryset=Workout.objects.all(),
        source="workout",
    )


class StartExerciseSerializer(serializers.Serializer):
    workout_exercise_id = serializers.PrimaryKeyRelatedField(
        queryset=WorkoutExercise.objects.all(),
        source="workout_exercise",
    )
    session_id = serializers.PrimaryKeyRelatedField(
        queryset=WorkoutCompletionRecord.objects.all(),
        source="session",
    )


class CompleteSetSerializer(serializers.Serializer):
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
