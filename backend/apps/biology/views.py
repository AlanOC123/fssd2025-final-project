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
    serializer_class = MuscleGroupSerializer
    queryset = MuscleGroup.objects.all()


class MuscleViewSet(NormalisedLookupViewSet):
    queryset = Muscle.objects.select_related("anatomical_direction", "muscle_group")
    serializer_class = MuscleSerializer
