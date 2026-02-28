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


class WorkoutSetSerializer(serializers.ModelSerializer):
    class Meta:
        model = WorkoutSet
        fields = [
            "id",
            "reps_prescribed",
            "weight_prescribed",
            "set_order",
        ]


class WorkoutExerciseSerializer(serializers.ModelSerializer):
    exercise = ExerciseSerializer(read_only=True)
    sets = WorkoutSetSerializer(read_only=True, many=True)

    class Meta:
        model = WorkoutExercise
        fields = ["id", "sets_prescribed", "order", "exercise", "sets"]


class WorkoutSerializer(serializers.ModelSerializer):
    program_phase = ProgramPhaseSerializer(read_only=True)
    exercises = WorkoutExerciseSerializer(read_only=True, many=True)

    class Meta:
        model = Workout
        fields = [
            "id",
            "workout_name",
            "estimated_duration_s",
            "scheduled_for",
            "trainer_notes",
            "program_phase",
            "exercises",
        ]


class WorkoutSetCompletionRecordSerializer(serializers.ModelSerializer):
    workout_set = WorkoutSetSerializer(read_only=True)

    workout_set_id = serializers.PrimaryKeyRelatedField(
        queryset=WorkoutSet.objects.all(), source="workout_set", write_only=True
    )

    exercise_completion_record_id = serializers.PrimaryKeyRelatedField(
        queryset=WorkoutExerciseCompletionRecord.objects.all(),
        source="exercise_completion_record",
        write_only=True,
    )

    class Meta:
        model = WorkoutSetCompletionRecord
        fields = [
            "id",
            "reps_completed",
            "weight_completed",
            "completed_at",
            "is_skipped",
            "workout_set",
            "workout_set_id",
            "reps_in_reserve",
            "exercise_completion_record_id",
        ]

        extra_kwargs = {"id": {"read_only": False, "required": False}}


class WorkoutExerciseCompletionRecordSerializer(serializers.ModelSerializer):
    completed_sets = WorkoutSetCompletionRecordSerializer(read_only=True, many=True)

    workout_exercise = WorkoutExerciseSerializer(read_only=True)
    workout_exercise_id = serializers.PrimaryKeyRelatedField(
        queryset=WorkoutExercise.objects.all(),
        source="workout_exercise",
        write_only=True,
    )

    workout_completion_record_id = serializers.PrimaryKeyRelatedField(
        queryset=WorkoutCompletionRecord.objects.all(),
        source="workout_completion_record",
        write_only=True,
    )

    class Meta:
        model = WorkoutExerciseCompletionRecord
        fields = [
            "id",
            "completed_sets",
            "workout_exercise",
            "workout_exercise_id",
            "workout_completion_record_id",
            "completed_at",
            "is_skipped",
            "difficulty_rating",
        ]

        extra_kwargs = {"id": {"read_only": False, "required": False}}


class WorkoutCompletionRecordSerializer(serializers.ModelSerializer):
    workout = WorkoutSerializer(read_only=True)
    workout_id = serializers.PrimaryKeyRelatedField(
        queryset=Workout.objects.all(), source="workout", write_only=True
    )
    exercise_records = WorkoutExerciseCompletionRecordSerializer(
        read_only=True, many=True
    )

    class Meta:
        model = WorkoutCompletionRecord
        fields = [
            "id",
            "time_taken_s",
            "completed_at",
            "is_skipped",
            "workout",
            "workout_id",
            "exercise_records",
        ]

        extra_kwargs = {"id": {"read_only": False, "required": False}}

    def create(self, validated_data):
        return super().create(validated_data)
