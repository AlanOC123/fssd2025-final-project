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
    """ViewSet for viewing and interacting with Equipment reference data.

    Inherits from NormalisedLookupViewSet to provide standard lookup functionality.
    """

    serializer_class = EquipmentSerializer
    queryset = Equipment.objects.all()


class ExerciseViewSet(viewsets.ReadOnlyModelViewSet):
    """ViewSet for public reference data of Exercises.

    This ViewSet is primarily used to browse and select exercises for workout
    construction. It supports filtering, searching, and ordering by exercise name.

    Attributes:
        permission_classes: Set to AllowAny for public read access.
        serializer_class: Uses ExerciseSerializer for detailed output.
        queryset: Optimized QuerySet using select_related and prefetch_related
             to reduce database hits for experience levels and equipment.
        filter_backends: Supports DjangoFilterBackend, SearchFilter, and
            OrderingFilter.
        filterset_class: Linked to ExerciseFilter for complex muscle-based filtering.
        search_fields: Enables searching on the 'exercise_name' field.
        ordering_fields: Allows ordering by 'exercise_name'.
        ordering: Default sort order is alphabetical by 'exercise_name'.
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
