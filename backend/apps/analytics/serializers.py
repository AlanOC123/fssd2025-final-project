from rest_framework import serializers


class MuscleLoadSerializer(serializers.Serializer):
    """Serializer for individual muscle load contributions.

    This serializer breaks down the load impact on a specific muscle,
    including its role (agonist, etc.) and associated muscle group.
    """

    muscle_id = serializers.UUIDField(source="muscle.id")
    muscle_label = serializers.CharField(source="muscle.label")
    muscle_group = serializers.CharField(
        source="muscle.muscle_group.label", allow_null=True
    )
    role = serializers.CharField()
    load = serializers.DecimalField(max_digits=10, decimal_places=2)


class ExerciseLoadHistorySerializer(serializers.Serializer):
    """Serializer for per-session load entries for a specific exercise.

    Used primarily to drive historical load charts on the trainer dashboard,
    providing a comprehensive view of session performance and muscle breakdown.
    """

    session_id = serializers.UUIDField()
    workout_name = serializers.CharField()
    completed_at = serializers.DateTimeField()
    total_load = serializers.DecimalField(max_digits=10, decimal_places=2)
    one_rep_max = serializers.DecimalField(max_digits=6, decimal_places=2)
    session_load = serializers.DecimalField(max_digits=10, decimal_places=2)
    muscle_breakdown = MuscleLoadSerializer(many=True)


class NextSessionRecommendationSerializer(serializers.Serializer):
    """Serializer for next session prescription windows.

    Provides trainers with specific load targets and weight ranges (floor/ceiling)
    based on historical performance and progression caps to guide future
    programming.
    """

    exercise_id = serializers.UUIDField(source="exercise.id")
    exercise_name = serializers.CharField(source="exercise.exercise_name")
    one_rep_max = serializers.DecimalField(max_digits=6, decimal_places=2)
    last_session_load = serializers.DecimalField(max_digits=10, decimal_places=2)
    target_load = serializers.DecimalField(
        max_digits=10, decimal_places=2, allow_null=True
    )
    rep_range_min = serializers.IntegerField()
    rep_range_max = serializers.IntegerField()
    weight_floor = serializers.DecimalField(
        max_digits=6, decimal_places=2, allow_null=True
    )
    weight_ceiling = serializers.DecimalField(
        max_digits=6, decimal_places=2, allow_null=True
    )
    progression_cap_percent = serializers.DecimalField(max_digits=4, decimal_places=2)


class ExerciseSnapshotSerializer(serializers.Serializer):
    """Serializer for stored ExerciseSessionSnapshot model instances.

    Used by the load history views to expose captured metrics from specific
    completed sessions when snapshot data is available.
    """

    session_id = serializers.UUIDField(source="session.id")
    workout_name = serializers.CharField(source="session.workout.workout_name")
    completed_at = serializers.DateTimeField(source="session.completed_at")
    one_rep_max = serializers.DecimalField(max_digits=6, decimal_places=2)
    session_load = serializers.DecimalField(max_digits=10, decimal_places=2)
    target_load = serializers.DecimalField(
        max_digits=10, decimal_places=2, allow_null=True
    )
    weight_floor = serializers.DecimalField(
        max_digits=6, decimal_places=2, allow_null=True
    )
    weight_ceiling = serializers.DecimalField(
        max_digits=6, decimal_places=2, allow_null=True
    )
