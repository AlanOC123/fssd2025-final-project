from decimal import Decimal

from rest_framework import generics, permissions, status
from rest_framework.exceptions import NotFound, PermissionDenied
from rest_framework.response import Response

from apps.analytics.models import ExerciseSessionSnapshot
from apps.analytics.serializers import (
    ExerciseSnapshotSerializer,
    NextSessionRecommendationSerializer,
)
from apps.analytics.services.load import calculate_joint_load, calculate_muscle_load
from apps.exercises.models import Exercise
from apps.programs.models import Program


def _get_program_for_trainer(program_id, trainer_user):
    try:
        program = Program.objects.select_related(
            "trainer_client_membership__trainer__user",
            "trainer_client_membership__client",
            "experience_level",
            "training_goal",
        ).get(pk=program_id)
    except Program.DoesNotExist:
        raise NotFound("Program not found.")

    if program.trainer_client_membership is None:
        raise NotFound("Program is not attached to a membership.")

    if program.trainer_client_membership.trainer.user != trainer_user:
        raise PermissionDenied("You can only view analytics for your own clients.")

    return program


class ExerciseLoadHistoryView(generics.GenericAPIView):
    """
    Returns the stored load history for a specific exercise within a program.

    Reads from ExerciseSessionSnapshot — fast, pre-computed, ordered
    chronologically. Each entry also computes the muscle-level breakdown
    on the fly since that depends on the exercise's joint/muscle data
    which is static reference data.

    Query params:
    - muscle_group (optional): filter breakdown to a specific muscle group label
    - role (optional): filter breakdown by muscle role code (AGONIST, SYNERGIST etc.)
    """

    permission_classes = [permissions.IsAuthenticated]
    serializer_class = ExerciseSnapshotSerializer

    def get(self, request, program_id, exercise_id):
        if not request.user.is_trainer:
            raise PermissionDenied("Only trainers can access analytics.")

        program = _get_program_for_trainer(program_id, request.user)

        try:
            exercise = Exercise.objects.prefetch_related(
                "exercise_movements__joint_contributions__joint_action__muscles__muscle__muscle_group",
                "exercise_movements__joint_contributions__joint_action__muscles__role",
                "exercise_movements__joint_contributions__joint_range_of_motion",
            ).get(pk=exercise_id)
        except Exercise.DoesNotExist:
            raise NotFound("Exercise not found.")

        snapshots = (
            ExerciseSessionSnapshot.objects.filter(program=program, exercise=exercise)
            .select_related(
                "session",
                "session__workout",
            )
            .order_by("session__completed_at")
        )

        if not snapshots.exists():
            return Response(
                {"detail": "No session data available for this exercise yet."},
                status=status.HTTP_204_NO_CONTENT,
            )

        # Build joint contributions once — same for every session
        joint_contributions = [
            jc
            for movement in exercise.exercise_movements.all()
            for jc in movement.joint_contributions.all()
        ]

        muscle_group_filter = request.query_params.get("muscle_group")
        role_filter = request.query_params.get("role")

        results = []
        for snapshot in snapshots:
            joint_loads = calculate_joint_load(
                snapshot.session_load, joint_contributions
            )
            muscle_loads = calculate_muscle_load(joint_loads)

            if muscle_group_filter:
                muscle_loads = [
                    m
                    for m in muscle_loads
                    if m["muscle"].muscle_group
                    and m["muscle"].muscle_group.label == muscle_group_filter
                ]
            if role_filter:
                muscle_loads = [
                    m for m in muscle_loads if m["role"] == role_filter.upper()
                ]

            entry = ExerciseSnapshotSerializer(snapshot).data
            entry["muscle_breakdown"] = [
                {
                    "muscle_id": str(m["muscle"].id),
                    "muscle_label": m["muscle"].label,
                    "muscle_group": (
                        m["muscle"].muscle_group.label
                        if m["muscle"].muscle_group
                        else None
                    ),
                    "role": m["role"],
                    "load": str(m["load"].quantize(Decimal("0.01"))),
                }
                for m in muscle_loads
            ]
            results.append(entry)

        return Response(results)


class NextSessionRecommendationView(generics.GenericAPIView):
    """
    Returns the next session recommendation for a specific exercise
    derived from the most recent stored snapshot.

    The snapshot already contains 1RM, target load, and weight band so
    this is a simple lookup — no recalculation needed.
    """

    permission_classes = [permissions.IsAuthenticated]
    serializer_class = NextSessionRecommendationSerializer

    def get(self, request, program_id, exercise_id):
        if not request.user.is_trainer:
            raise PermissionDenied("Only trainers can access analytics.")

        program = _get_program_for_trainer(program_id, request.user)

        try:
            exercise = Exercise.objects.get(pk=exercise_id)
        except Exercise.DoesNotExist:
            raise NotFound("Exercise not found.")

        latest_snapshot = (
            ExerciseSessionSnapshot.objects.filter(program=program, exercise=exercise)
            .select_related("session")
            .order_by("-session__completed_at")
            .first()
        )

        if not latest_snapshot:
            return Response(
                {"detail": "No completion data available for this exercise yet."},
                status=status.HTTP_204_NO_CONTENT,
            )

        training_goal = program.training_goal
        experience_level = program.experience_level

        data = {
            "exercise": exercise,
            "one_rep_max": latest_snapshot.one_rep_max,
            "last_session_load": latest_snapshot.session_load,
            "target_load": latest_snapshot.target_load,
            "rep_range_min": training_goal.rep_range_min,
            "rep_range_max": training_goal.rep_range_max,
            "weight_floor": latest_snapshot.weight_floor,
            "weight_ceiling": latest_snapshot.weight_ceiling,
            "progression_cap_percent": experience_level.progression_cap_percent,
        }

        serializer = self.get_serializer(data)
        return Response(serializer.data)
