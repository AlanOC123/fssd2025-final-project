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


class PlaneOfMotionViewset(SuperUserRestrictedMixin, ReadOnlyModelViewSet):
    """
    Restricted view of Planes of Motion.
    Used to verify Plane of Motion for dependant models
    """

    permission_classes = [permissions.AllowAny]
    serializer_class = PlaneOfMotionSerializer
    queryset = PlaneOfMotion.objects.all()


class AnatomicalDirectionViewset(ReadOnlyModelViewSet):
    """
    Viewset for Anatomical Directions.
    Set up to allow searching of exercises based on direction name
    """

    permission_classes = [permissions.AllowAny]
    serializer_class = AnatomicalDirectionSerializer
    queryset = AnatomicalDirection.objects.all()

    filter_backends = [filters.SearchFilter]
    search_fields = ["direction_name"]


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


class MuscleViewset(ReadOnlyModelViewSet):
    """
    Viewset for Muscles.
    Set up to allow searching of exercises based on direction name
    """

    permission_classes = [permissions.AllowAny]
    serializer_class = MuscleSerializer
    queryset = Muscle.objects.all()

    filter_backends = [filters.SearchFilter]
    search_fields = ["muscle_name"]


class MuscleRoleViewset(SuperUserRestrictedMixin, ReadOnlyModelViewSet):
    """
    Restricted view of Muscle Roles.
    Used to verify Muscle Roles for dependant models
    """

    permission_classes = [permissions.AllowAny]
    serializer_class = MuscleRoleSerializer
    queryset = MuscleRole.objects.all()
