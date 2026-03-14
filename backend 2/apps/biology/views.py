from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import filters, permissions
from rest_framework.viewsets import (
    ReadOnlyModelViewSet,
)

from core.mixins import SuperUserRestrictedMixin

from .models import (
    AnatomicalDirection,
    Joint,
    JointAction,
    MovementPattern,
    Muscle,
    MuscleInvolvement,
    MuscleRole,
    PlaneOfMotion,
)
from .serializers import (
    AnatomicalDirectionSerializer,
    JointActionSerializer,
    JointSerializer,
    MovementPatternSerializer,
    MuscleInvolvementSerializer,
    MuscleRoleSerializer,
    MuscleSerializer,
    PlaneOfMotionSerializer,
)

# Public Viewsets


class MuscleViewset(ReadOnlyModelViewSet):
    """
    Public Reference Data: Muscles
    Used to populate 'Target Muscle' dropdowns.
    """

    # Allow public access
    permission_classes = [permissions.AllowAny]
    serializer_class = MuscleSerializer
    queryset = Muscle.objects.all()

    # Filters and Searching
    filter_backends = [filters.SearchFilter, DjangoFilterBackend]
    search_fields = ["muscle_name"]
    filterset_fields = ["anatomical_direction"]


class MuscleRoleViewset(ReadOnlyModelViewSet):
    """
    Public Reference Data: Roles
    Used to populate 'Role' dropdowns (Agonist vs Synergist).
    """

    permission_classes = [permissions.AllowAny]
    filter_backends = [filters.SearchFilter, DjangoFilterBackend]
    serializer_class = MuscleRoleSerializer
    queryset = MuscleRole.objects.all()

    search_fields = ["role_name"]
    filterset_fields = ["role_name"]


class AnatomicalDirectionViewset(ReadOnlyModelViewSet):
    """
    Public Reference Data: Directions
    Used to populate 'Body Region' dropdowns (Anterior/Posterior).
    """

    permission_classes = [permissions.AllowAny]
    serializer_class = AnatomicalDirectionSerializer
    queryset = AnatomicalDirection.objects.all()

    filter_backends = [filters.SearchFilter]
    search_fields = ["direction_name"]
    filterset_fields = ["direction_name"]


# Private Viewsets


class PlaneOfMotionViewset(SuperUserRestrictedMixin, ReadOnlyModelViewSet):
    """
    Restricted view of Planes of Motion.
    Used to verify Plane of Motion for dependant models
    """

    permission_classes = [permissions.AllowAny]
    serializer_class = PlaneOfMotionSerializer
    queryset = PlaneOfMotion.objects.all()


class JointViewset(SuperUserRestrictedMixin, ReadOnlyModelViewSet):
    """
    Restricted view of Joints.
    Used to verify Joints for dependant models
    """

    permission_classes = [permissions.AllowAny]
    serializer_class = JointSerializer
    queryset = Joint.objects.all()


class JointActionViewset(SuperUserRestrictedMixin, ReadOnlyModelViewSet):
    """
    Restricted view of Joint Actions.
    Used to verify Joint Actions for dependant models
    """

    permission_classes = [permissions.AllowAny]
    serializer_class = JointActionSerializer
    queryset = JointAction.objects.all()


class MovementPatternViewset(SuperUserRestrictedMixin, ReadOnlyModelViewSet):
    """
    Restricted view of Movement Patterns.
    Used to verify Movement Patterns for dependant models
    """

    permission_classes = [permissions.AllowAny]
    serializer_class = MovementPatternSerializer
    queryset = MovementPattern.objects.all()


class MuscleInvolvementViewset(SuperUserRestrictedMixin, ReadOnlyModelViewSet):
    """
    Restricted view of Muscle Involvements.
    Used to verify Muscle Involvements for dependant models
    """

    serializer_class = MuscleInvolvementSerializer
    permission_classes = [permissions.AllowAny]
    queryset = MuscleInvolvement.objects.all()
