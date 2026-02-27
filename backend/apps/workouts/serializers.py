from rest_framework import serializers

from apps.exercises.serializers import ExerciseSerializer
from apps.programs.serializers import ProgramPhaseSerializer

from .models import (
    Workout,
    WorkoutCompletionRecord,
    WorkoutExercise,
    WorkoutExerciseCompletionRecord,
    WorkoutSet,
    WorkoutSetCompletionRecord,
)


class WorkoutSerializer(serializers.ModelSerializer):

    program_phase = ProgramPhaseSerializer(read_only=True)

    class Meta:
        model = Workout
        fields = [
            "id",
            "workout_name",
            "estimated_duration_s",
            "scheduled_for",
            "trainer_notes",
            "program_phase",
        ]


class WorkoutExerciseSerializer(serializers.ModelSerializer):
    exercise = ExerciseSerializer(read_only=True)
    workout_id = serializers.PrimaryKeyRelatedField(source="workout", read_only=True)

    class Meta:
        model = WorkoutExercise
        fields = ["id", "sets_prescribed", "order", "workout_id", "exercise"]


class WorkoutSetSerializer(serializers.ModelSerializer):
    workout_exercise_id = serializers.PrimaryKeyRelatedField(
        source="workout_exercise", read_only=True
    )

    class Meta:
        model = WorkoutSet
        fields = [
            "reps_prescribed",
            "weight_prescribed",
            "set_order",
            "workout_exercise",
        ]


class WorkoutCompletionRecordSerializer(serializers.ModelSerializer):
    workout_id = serializers.PrimaryKeyRelatedField(source="workout", read_only=True)

    class Meta:
        model = WorkoutCompletionRecord
        fields = ["time_taken_s", "completed_at", "is_skipped", "workout_id"]


class WorkoutExerciseCompletionRecordSerializer(serializers.ModelSerializer):
    workout_completion_record_id = serializers.PrimaryKeyRelatedField(
        source="workout_completion_record", read_only=True
    )
    workout_exercise_id = serializers.PrimaryKeyRelatedField(
        source="workout_exercise", read_only=True
    )

    class Meta:
        model = WorkoutExerciseCompletionRecord
        fields = [
            "id",
            "workout_completion_record_id",
            "workout_exercise_id",
            "completed_at",
            "is_skipped",
            "difficulty_rating",
        ]


class WorkoutSetCompletionRecordSerializer(serializers.ModelSerializer):
    workout_set_id = serializers.PrimaryKeyRelatedField(
        source="workout_set", read_only=True
    )
    exercise_completion_record_id = serializers.PrimaryKeyRelatedField(
        source="exercise_completion_record", read_only=True
    )

    class Meta:
        model = WorkoutSetCompletionRecord
        fields = [
            "id",
            "reps_completed",
            "weight_completed",
            "completed_at",
            "is_skipped",
            "workout_set_id",
            "exercise_completion_record_id",
            "reps_in_reserve",
        ]
