from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import filters, permissions, viewsets

from core.permissions import IsTrainerOrReadOnly

from .models import (
    Workout,
    WorkoutCompletionRecord,
    WorkoutExercise,
    WorkoutExerciseCompletionRecord,
    WorkoutSet,
    WorkoutSetCompletionRecord,
)
from .serializers import (
    WorkoutCompletionRecordSerializer,
    WorkoutExerciseCompletionRecordSerializer,
    WorkoutExerciseSerializer,
    WorkoutSerializer,
    WorkoutSetCompletionRecordSerializer,
    WorkoutSetSerializer,
)


class WorkoutViewset(viewsets.ModelViewSet):
    serializer_class = WorkoutSerializer
    permission_classes = [permissions.IsAuthenticated, IsTrainerOrReadOnly]

    filter_backends = [DjangoFilterBackend, filters.SearchFilter]
    search_fields = ["workout_name"]
    filterset_fields = ["program_phase", "scheduled_for"]

    ordering_fields = ["created_at", "scheduled_for"]
    ordering = ["scheduled_for"]

    def get_queryset(self):
        user = self.request.user

        queryset = Workout.objects.prefetch_related(
            "exercises", "exercises__exercise", "exercises__sets"
        )

        if user.is_trainer:
            return queryset.filter(
                program_phase__program__trainer_client_membership__trainer=user.trainer_profile
            ).distinct()

        elif user.is_client:
            return queryset.filter(
                program_phase__program__trainer_client_membership__client=user.client_profile
            ).distinct()

        return Workout.objects.none()


class WorkoutExerciseViewset(viewsets.ModelViewSet):
    serializer_class = WorkoutExerciseSerializer
    permission_classes = [permissions.IsAuthenticated, IsTrainerOrReadOnly]

    def get_queryset(self):
        user = self.request.user

        queryset = WorkoutExercise.objects.select_related(
            "workout", "exercise"
        ).prefetch_related("sets")

        if user.is_trainer:
            return queryset.filter(
                workout__program_phase__program__trainer_client_membership__trainer=user.trainer_profile
            ).distinct()

        elif user.is_client:
            return queryset.filter(
                workout__program_phase__program__trainer_client_membership__client=user.client_profile
            ).distinct()

        return WorkoutExercise.objects.none()


class WorkoutSetViewset(viewsets.ModelViewSet):
    serializer_class = WorkoutSetSerializer
    permission_classes = [permissions.IsAuthenticated, IsTrainerOrReadOnly]

    def get_queryset(self):
        user = self.request.user

        queryset = WorkoutSet.objects.select_related(
            "workout_exercise", "workout_exercise__workout"
        )

        if user.is_trainer:
            return queryset.filter(
                workout_exercise__workout__program_phase__program__trainer_client_membership__trainer=user.trainer_profile
            ).distinct()

        elif user.is_client:
            return queryset.filter(
                workout_exercise__workout__program_phase__program__trainer_client_membership__client=user.client_profile
            ).distinct()

        return WorkoutSet.objects.none()


class WorkoutCompletionRecordViewset(viewsets.ModelViewSet):
    serializer_class = WorkoutCompletionRecordSerializer
    permission_classes = [permissions.IsAuthenticated]

    filter_backends = [DjangoFilterBackend, filters.SearchFilter]

    search_fields = ["workout__workout_name"]
    filterset_fields = ["is_skipped", "completed_at"]

    def get_queryset(self):
        user = self.request.user

        queryset = WorkoutCompletionRecord.objects.select_related(
            "workout"
        ).prefetch_related(
            "exercise_records",
            "exercise_records__workout_exercise",
            "exercise_records__workout_exercise__exercise",
            "exercise_records__completed_sets",
            "exercise_records__completed_sets__workout_set",
        )

        if user.is_trainer:
            return queryset.filter(
                workout__program_phase__program__trainer_client_membership__trainer=user.trainer_profile
            ).distinct()

        elif user.is_client:
            return queryset.filter(
                workout__program_phase__program__trainer_client_membership__client=user.client_profile
            ).distinct()

        return WorkoutCompletionRecord.objects.none()


class WorkoutExerciseCompletionViewset(viewsets.ModelViewSet):
    serializer_class = WorkoutExerciseCompletionRecordSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        user = self.request.user

        queryset = WorkoutExerciseCompletionRecord.objects.select_related(
            "workout_exercise", "workout_completion_record"
        )

        if user.is_trainer:
            return queryset.filter(
                workout_completion_record__workout__program_phase__program__trainer_client_membership__trainer=user.trainer_profile
            ).distinct()

        elif user.is_client:
            return queryset.filter(
                workout_completion_record__workout__program_phases__program__trainer_client_membership__client=user.client_profile
            ).distinct()

        return WorkoutExerciseCompletionRecord.objects.none()


class WorkoutSetCompletionRecordViewset(viewsets.ModelViewSet):
    serializer_class = WorkoutSetCompletionRecordSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        user = self.request.user

        queryset = WorkoutSetCompletionRecord.objects.select_related(
            "workout_set", "exercise_completion_record"
        )

        if user.is_trainer:
            return queryset.filter(
                exercise_completion_record__workout_completion_record__workout__program_phase__program__trainer_client_membership__trainer=user.trainer_profile
            ).distinct()

        elif user.is_client:
            return queryset.filter(
                exercise_completion_record__workout_completion_record__workout__program_phases__program__trainer_client_membership__client=user.client_profile
            ).distinct()

        return WorkoutSetCompletionRecord.objects.none()
