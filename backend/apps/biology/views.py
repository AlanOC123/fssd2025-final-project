from core.views import NormalisedLookupViewSet

from .models import (
    Muscle,
    MuscleGroup,
)
from .serializers import (
    MuscleGroupSerializer,
    MuscleSerializer,
)


class MuscleGroupViewSet(NormalisedLookupViewSet):
    """ViewSet for managing muscle group lookup data.

    Provides standard CRUD operations via NormalisedLookupViewSet, ensuring
    standardized normalization and search behavior for muscle group records.
    """

    serializer_class = MuscleGroupSerializer
    queryset = MuscleGroup.objects.all()


class MuscleViewSet(NormalisedLookupViewSet):
    """ViewSet for managing individual muscle records.

    Inherits from NormalisedLookupViewSet to provide standard API behavior.
    Optimizes database performance by utilizing select_related to prefetch
    associated anatomical directions and muscle groups in a single query.
    """

    # Optimize query with select_related for related biological metadata.
    queryset = Muscle.objects.select_related("anatomical_direction", "muscle_group")
    serializer_class = MuscleSerializer
