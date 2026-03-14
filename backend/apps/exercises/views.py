from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import filters, permissions, viewsets

from core.views import NormalisedLookupViewSet

from .filters import ExerciseFilter
from .models import (
    Equipment,
    Exercise,
)
from .serializers import (
    EquipmentSerializer,
    ExerciseSerializer,
)


class EquipmentViewSet(NormalisedLookupViewSet):
    serializer_class = EquipmentSerializer
    queryset = Equipment.objects.all()


class ExerciseViewSet(viewsets.ReadOnlyModelViewSet):
    """
    Public Reference Data: Exercise
    Used to select exercises to build workouts.
    """

    permission_classes = [permissions.AllowAny]
    serializer_class = ExerciseSerializer
    queryset = (
        Exercise.objects.select_related("experience_level")
        .prefetch_related("equipment")
        .distinct()
    )

    filter_backends = [
        DjangoFilterBackend,
        filters.SearchFilter,
        filters.OrderingFilter,
    ]
    filterset_class = ExerciseFilter

    search_fields = ["exercise_name"]

    ordering_fields = ["exercise_name"]
    ordering = ["exercise_name"]
