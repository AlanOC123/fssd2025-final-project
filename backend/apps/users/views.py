from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import permissions
from rest_framework.viewsets import ModelViewSet, ReadOnlyModelViewSet

from .filters import TrainerClientMembershipFilter
from .models import (
    ExperienceLevel,
    MembershipStatus,
    TrainerClientMembership,
    TrainingGoal,
)
from .serializers import (
    ExperienceLevelSerializer,
    MembershipStatusSerializer,
    TrainerClientMembershipSerializer,
    TrainingGoalSerializer,
)


# Protected Viewsets
class TrainerClientMembershipViewset(ModelViewSet):
    serializer_class = TrainerClientMembershipSerializer
    permission_classes = [permissions.IsAuthenticated]

    filter_backends = [DjangoFilterBackend]
    filterset_class = TrainerClientMembershipFilter

    def get_queryset(self):
        # Get the user from the request
        user = self.request.user

        # The user is a trainer
        if user.is_trainer:
            return TrainerClientMembership.objects.filter(trainer=user.trainer_profile)

        # The user is a client
        elif user.is_client:
            return TrainerClientMembership.objects.filter(client=user.client_profile)

        # The user is unknown
        else:
            return TrainerClientMembership.objects.none()


# Public Viewsets
class TrainingGoalViewset(ReadOnlyModelViewSet):
    serializer_class = TrainingGoalSerializer
    queryset = TrainingGoal.objects.all()
    permission_classes = [permissions.AllowAny]


class ExperienceLevelViewset(ReadOnlyModelViewSet):
    serializer_class = ExperienceLevelSerializer
    queryset = ExperienceLevel.objects.all()
    permission_classes = [permissions.AllowAny]


class MembershipStatusViewset(ReadOnlyModelViewSet):
    serializer_class = MembershipStatusSerializer
    queryset = MembershipStatus.objects.all()
    permission_classes = [permissions.AllowAny]
