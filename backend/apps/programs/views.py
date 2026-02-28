from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import filters, permissions, viewsets

from apps.programs.models import Program, ProgramPhase, ProgramPhaseOption
from apps.programs.serializers import (
    ProgramPhaseOptionSerializer,
    ProgramPhaseSerializer,
    ProgramSerializer,
)
from core.permissions import IsTrainerOrReadOnly


# Protected Viewsets
class ProgramViewSet(viewsets.ModelViewSet):
    serializer_class = ProgramSerializer
    permission_classes = [permissions.IsAuthenticated, IsTrainerOrReadOnly]

    filter_backends = [DjangoFilterBackend, filters.SearchFilter]
    search_fields = ["program_name"]

    filterset_fields = [
        "training_goal",
        "experience_level",
        "trainer_client_membership",
    ]

    def get_queryset(self):
        user = self.request.user

        queryset = Program.objects.select_related(
            "training_goal", "experience_level"
        ).prefetch_related("phases__phase_option")

        if user.is_trainer:
            return queryset.filter(
                trainer_client_membership__trainer=user.trainer_profile
            )

        elif user.is_client:
            return queryset.filter(
                trainer_client_membership__client=user.client_profile
            )

        return Program.objects.none()


class ProgramPhaseViewset(viewsets.ModelViewSet):
    serializer_class = ProgramPhaseSerializer
    permission_classes = [permissions.IsAuthenticated, IsTrainerOrReadOnly]

    filter_backends = [DjangoFilterBackend]
    filterset_fields = ["is_active", "is_completed", "program"]

    def get_queryset(self):
        user = self.request.user

        queryset = ProgramPhase.objects.select_related(
            "program", "program__trainer_client_membership", "phase_option"
        )

        if user.is_trainer:
            return queryset.filter(
                program__trainer_client_membership__trainer=user.trainer_profile
            )

        elif user.is_client:
            return queryset.filter(
                program__trainer_client_membership__client=user.client_profile
            )

        return ProgramPhase.objects.none()


# Public Viewsets
class ProgramPhaseOptionViewset(viewsets.ReadOnlyModelViewSet):
    serializer_class = ProgramPhaseOptionSerializer
    permission_classes = [permissions.AllowAny]

    filter_backends = [DjangoFilterBackend]
    filterset_fields = ["phase_name"]

    queryset = ProgramPhaseOption.objects.all()
