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


# Public Viewsets
class EquipmentViewset(viewsets.ReadOnlyModelViewSet):
    """
    Public Reference Data: Equipment
    Used to populate 'Equipment' dropdowns (Barbell, Dumbbell, etc).
    """

    serializer_class = EquipmentSerializer
    permission_classes = [permissions.AllowAny]
    queryset = Equipment.objects.all()

    filter_backends = [filters.SearchFilter, DjangoFilterBackend]
    search_fields = ["equipment_name"]


class ExerciseViewset(viewsets.ReadOnlyModelViewSet):
    """
    Public Reference Data: Exercise
    Used to select exercises to build workouts.
    """

    permission_classes = [permissions.AllowAny]
    serializer_class = ExerciseSerializer
    queryset = Exercise.objects.prefetch_related(
        "equipment", "experience_level"
    ).distinct()

    filter_backends = [DjangoFilterBackend, filters.SearchFilter]
    filterset_class = ExerciseFilter

    search_fields = ["exercise_name"]


# Private Viewsets


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
