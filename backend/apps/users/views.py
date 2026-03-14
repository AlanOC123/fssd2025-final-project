from django.shortcuts import get_object_or_404
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import filters, mixins, permissions, status, viewsets
from rest_framework.decorators import action
from rest_framework.exceptions import PermissionDenied
from rest_framework.response import Response

from core.views import NormalisedLookupViewSet

from .constants import MembershipVocabulary
from .filters import TrainerClientMembershipFilter
from .models import (
    ExperienceLevel,
    TrainerClientMembership,
    TrainerProfile,
    TrainingGoal,
)
from .serializers import (
    ExperienceLevelSerializer,
    MembershipRequestSerializer,
    TrainerClientMembershipSerializer,
    TrainerProfileSerializer,
    TrainingGoalSerializer,
)
from .services.membership import MembershipService


# Protected Viewsets
class TrainerClientMembershipViewset(
    mixins.ListModelMixin, mixins.RetrieveModelMixin, viewsets.GenericViewSet
):
    serializer_class = TrainerClientMembershipSerializer
    permission_classes = [permissions.IsAuthenticated]

    filter_backends = [DjangoFilterBackend]
    filterset_class = TrainerClientMembershipFilter

    def get_queryset(self):

        queryset = TrainerClientMembership.objects.select_related(
            "trainer__user", "client__user", "status", "previous_membership"
        )
        # Get the user from the request
        user = self.request.user

        # The user is a trainer
        if user.is_trainer:
            return queryset.filter(trainer=user.trainer_profile)

        # The user is a client
        if user.is_client:
            return queryset.filter(client=user.client_profile)

        # The user is unknown
        return queryset.none()

    def _handle_client_membership_action(self, request, service_action):
        client_user = request.user

        if not client_user.is_client:
            raise PermissionDenied("Only clients can initiate a membership request.")

        action_serializer = MembershipRequestSerializer(data=request.data)
        action_serializer.is_valid(raise_exception=True)

        trainer = get_object_or_404(
            TrainerProfile.objects.select_related("user"),
            pk=action_serializer.validated_data["trainer_id"],
        )

        membership = service_action(client_user=client_user, trainer_user=trainer.user)

        output = self.get_serializer(membership)
        return Response(output.data, status=status.HTTP_201_CREATED)

    def _handle_trainer_membership_action(
        self, request, service_action, action_message
    ):
        membership = self.get_object()
        trainer_user = request.user

        if not trainer_user.is_trainer:
            raise PermissionDenied(
                f"Only a trainer can {action_message} a pending request."
            )

        membership = service_action(membership=membership, trainer_user=trainer_user)

        serializer = self.get_serializer(membership)
        return Response(serializer.data, status=status.HTTP_200_OK)

    @action(detail=False, methods=["post"], url_path="request")
    def request_membership(self, request):
        return self._handle_client_membership_action(
            request=request, service_action=MembershipService.request
        )

    @action(detail=True, methods=["post"])
    def accept(self, request, pk=None):
        return self._handle_trainer_membership_action(
            request=request,
            service_action=MembershipService.accept,
            action_message="accept",
        )

    @action(detail=True, methods=["post"])
    def reject(self, request, pk=None):
        return self._handle_trainer_membership_action(
            request=request,
            service_action=MembershipService.reject,
            action_message="reject",
        )

    @action(detail=True, methods=["post"])
    def dissolve(self, request, pk=None):
        membership = self.get_object()
        membership = MembershipService.dissolve(
            membership=membership, acting_user=request.user
        )

        serializer = self.get_serializer(membership)
        return Response(serializer.data, status=status.HTTP_200_OK)

    @action(detail=False, methods=["post"], url_path="renew")
    def renew_membership(self, request):
        return self._handle_client_membership_action(
            request=request, service_action=MembershipService.renew
        )


class TrainerMatchingViewset(viewsets.ReadOnlyModelViewSet):
    serializer_class = TrainerProfileSerializer
    permission_classes = [permissions.IsAuthenticated]

    filter_backends = [DjangoFilterBackend, filters.SearchFilter]
    search_fields = ["user__email", "company", "website"]

    def get_queryset(self):
        # Trainers cant search for other trainers
        user = self.request.user

        if user.is_trainer:
            return TrainerProfile.objects.none()

        if not user.is_client:
            return TrainerProfile.objects.none()

        profile = user.client_profile

        queryset = TrainerProfile.objects.select_related("user").prefetch_related(
            "accepted_goals",
            "accepted_levels",
        )

        return (
            queryset.filter(
                accepted_goals=profile.goal,
                accepted_levels=profile.level,
            )
            .distinct()
            .exclude(
                client_memberships__client=profile,
                client_memberships__status__code__in=[
                    MembershipVocabulary.PENDING,
                    MembershipVocabulary.ACTIVE,
                ],
            )
        )


# Public Viewsets
class TrainingGoalViewset(NormalisedLookupViewSet):
    serializer_class = TrainingGoalSerializer
    queryset = TrainingGoal.objects.all()


class ExperienceLevelViewset(NormalisedLookupViewSet):
    serializer_class = ExperienceLevelSerializer
    queryset = ExperienceLevel.objects.all()
