from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import filters, permissions, viewsets

from core.mixins import SuperUserRestrictedMixin

from .filters import ExerciseFilter
from .models import (
    Equipment,
    Exercise,
    ExerciseMovement,
    ExercisePhase,
    JointContribution,
    JointRangeOfMotion,
)
from .serializers import (
    EquipmentSerializer,
    ExerciseMovementSerializer,
    ExercisePhaseSerializer,
    ExerciseSerializer,
    JointContributionSerializer,
    JointRangeOfMotionSerializer,
)


class EquipmentViewset(viewsets.ReadOnlyModelViewSet):
    serializer_class = EquipmentSerializer
    permission_classes = [permissions.IsAuthenticated]
    queryset = Equipment.objects.all()

    filter_backends = [filters.SearchFilter]
    search_fields = ["equipment_name"]


class ExerciseViewset(viewsets.ReadOnlyModelViewSet):
    serializer_class = ExerciseSerializer
    queryset = Exercise.objects.prefetch_related(
        "equipment", "experience_level"
    ).distinct()

    filter_backends = [DjangoFilterBackend, filters.SearchFilter]

    filterset_class = ExerciseFilter

    search_fields = ["exercise_name"]


class ExerciseMovementViewset(SuperUserRestrictedMixin, viewsets.ReadOnlyModelViewSet):
    serializer_class = ExerciseMovementSerializer
    permission_classes = [permissions.AllowAny]
    queryset = ExerciseMovement.objects.all()


class ExercisePhaseViewset(SuperUserRestrictedMixin, viewsets.ReadOnlyModelViewSet):
    serializer_class = ExercisePhaseSerializer
    permission_classes = [permissions.AllowAny]
    queryset = ExercisePhase.objects.all()


class JointContributionViewset(SuperUserRestrictedMixin, viewsets.ReadOnlyModelViewSet):
    serializer_class = JointContributionSerializer
    permission_classes = [permissions.AllowAny]
    queryset = JointContribution.objects.all()


class JointRangeOfMotionViewset(
    SuperUserRestrictedMixin, viewsets.ReadOnlyModelViewSet
):
    serializer_class = JointRangeOfMotionSerializer
    permission_classes = [permissions.AllowAny]
    queryset = JointRangeOfMotion.objects.all()
