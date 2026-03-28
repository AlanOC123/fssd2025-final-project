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
    """Retrieves a program and validates trainer ownership.

    Args:
        program_id: The UUID of the program to retrieve.
        trainer_user: The user instance of the trainer making the request.

    Returns:
        Program: The program instance if found and authorized.

    Raises:
        NotFound: If the program does not exist or is not linked to a membership.
        PermissionDenied: If the requesting trainer is not the one assigned to
            the program's membership.
    """
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
    """API view to retrieve the historical load progression for an exercise.

    This view reads from pre-computed ExerciseSessionSnapshot records for speed.
    It performs on-the-fly muscle-level load breakdown calculations because
    joint/muscle mapping is considered static reference data.

    Query parameters:
        muscle_group (optional): Filter the breakdown to a specific muscle group.
        role (optional): Filter the breakdown by muscle role (e.g., AGONIST).
    """

    permission_classes = [permissions.IsAuthenticated]
    serializer_class = ExerciseSnapshotSerializer

    def get(self, request, program_id, exercise_id):
        """Handles GET requests for exercise load history.

        Args:
            request: The current HTTP request.
            program_id: The UUID of the program.
            exercise_id: The UUID of the exercise.

        Returns:
            Response: A list of serialized snapshots with muscle breakdown data.

        Raises:
            PermissionDenied: If the user is not a trainer.
            NotFound: If the program or exercise is not found.
        """
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

        # Pre-build joint contributions for the exercise to avoid redundant loops.
        joint_contributions = [
            jc
            for movement in exercise.exercise_movements.all()
            for jc in movement.joint_contributions.all()
        ]

        muscle_group_filter = request.query_params.get("muscle_group")
        role_filter = request.query_params.get("role")

        results = []
        for snapshot in snapshots:
            # Calculate how the session load distributed across joints and muscles.
            joint_loads = calculate_joint_load(
                snapshot.session_load, joint_contributions
            )
            muscle_loads = calculate_muscle_load(joint_loads)

            # Apply filters if provided via query parameters.
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

            # Serialize snapshot and attach the calculated breakdown.
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
    """API view to retrieve recommendations for the next exercise session.

    This view identifies the most recent performance snapshot and extracts
    computed targets (1RM, target load, and weight bands) to guide the
    trainer's programming for the next session.
    """

    permission_classes = [permissions.IsAuthenticated]
    serializer_class = NextSessionRecommendationSerializer

    def get(self, request, program_id, exercise_id):
        """Handles GET requests for next session recommendations.

        Args:
            request: The current HTTP request.
            program_id: The UUID of the program.
            exercise_id: The UUID of the exercise.

        Returns:
            Response: A serialized recommendation based on the latest performance.

        Raises:
            PermissionDenied: If the user is not a trainer.
            NotFound: If the program or exercise is not found.
        """
        if not request.user.is_trainer:
            raise PermissionDenied("Only trainers can access analytics.")

        program = _get_program_for_trainer(program_id, request.user)

        try:
            exercise = Exercise.objects.get(pk=exercise_id)
        except Exercise.DoesNotExist:
            raise NotFound("Exercise not found.")

        # Find the latest completed session snapshot for this exercise.
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

        # Package the snapshot data with the program's target rep range for display.
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
