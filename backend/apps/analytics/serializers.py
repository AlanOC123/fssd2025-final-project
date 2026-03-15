from rest_framework import serializers


class MuscleLoadSerializer(serializers.Serializer):
    muscle_id = serializers.UUIDField(source="muscle.id")
    muscle_label = serializers.CharField(source="muscle.label")
    muscle_group = serializers.CharField(
        source="muscle.muscle_group.label", allow_null=True
    )
    role = serializers.CharField()
    load = serializers.DecimalField(max_digits=10, decimal_places=2)


class ExerciseLoadHistorySerializer(serializers.Serializer):
    """
    Per-session load entry for a specific exercise.
    Used to drive the historic load chart on the trainer dashboard.
    """

    session_id = serializers.UUIDField()
    workout_name = serializers.CharField()
    completed_at = serializers.DateTimeField()
    total_load = serializers.DecimalField(max_digits=10, decimal_places=2)
    one_rep_max = serializers.DecimalField(max_digits=6, decimal_places=2)
    session_load = serializers.DecimalField(max_digits=10, decimal_places=2)
    muscle_breakdown = MuscleLoadSerializer(many=True)


class NextSessionRecommendationSerializer(serializers.Serializer):
    """
    Next session prescription window for a specific exercise.
    Provides the trainer with the load target and weight band to guide programming.
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
    """
    Serializes a stored ExerciseSessionSnapshot.
    Used by the load history view when snapshot data is available.
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
