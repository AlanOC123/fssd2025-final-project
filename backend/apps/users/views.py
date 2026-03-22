from django.shortcuts import get_object_or_404
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import filters, mixins, parsers, permissions, status, viewsets
from rest_framework.decorators import action
from rest_framework.exceptions import PermissionDenied
from rest_framework.response import Response

from core.views import NormalisedLookupViewSet

from .constants import MembershipVocabulary
from .filters import TrainerClientMembershipFilter
from .models import (
    ClientProfile,
    ExperienceLevel,
    TrainerClientMembership,
    TrainerProfile,
    TrainingGoal,
)
from .serializers import (
    ClientProfileSerializer,
    ExperienceLevelSerializer,
    MembershipRequestSerializer,
    TrainerClientMembershipSerializer,
    TrainerMatchingSerializer,
    TrainerProfileSerializer,
    TrainerProfileWriteSerializer,
    TrainingGoalSerializer,
)
from .services.membership import MembershipService


# Protected Viewsets
class TrainerClientMembershipViewSet(
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

        trainer = action_serializer.validated_data["trainer_id"]

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


class TrainerMatchingViewSet(viewsets.ReadOnlyModelViewSet):
    serializer_class = TrainerMatchingSerializer
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


class TrainerProfileViewSet(
    mixins.RetrieveModelMixin, mixins.UpdateModelMixin, viewsets.GenericViewSet
):
    permission_classes = [permissions.IsAuthenticated]
    http_method_names = ["get", "patch", "head", "options"]

    def get_queryset(self):
        return TrainerProfile.objects.select_related("user").prefetch_related(
            "accepted_goals", "accepted_levels"
        )

    def get_object(self):
        user = self.request.user

        if not user.is_trainer:
            raise PermissionDenied("Only trainers can access this endpoint.")

        return get_object_or_404(TrainerProfile, user=user)

    def get_serializer_class(self):
        if self.action in ("update", "partial_update", "me_update"):
            return TrainerProfileWriteSerializer
        return TrainerProfileSerializer

    def partial_update(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)

        # Handle M2M fields explicitly
        if "accepted_goals" in serializer.validated_data:
            instance.accepted_goals.set(serializer.validated_data.pop("accepted_goals"))
        if "accepted_levels" in serializer.validated_data:
            instance.accepted_levels.set(
                serializer.validated_data.pop("accepted_levels")
            )

        for attr, value in serializer.validated_data.items():
            setattr(instance, attr, value)
        instance.save()

        output = self.get_serializer(instance)
        return Response(output.data)

    @action(detail=False, methods=["get"], url_path="me")
    def me(self, request):
        instance = self.get_object()
        serializer = self.get_serializer(instance)
        return Response(serializer.data)

    @action(detail=False, methods=["patch"], url_path="me/update")
    def me_update(self, request):
        instance = self.get_object()
        print("=== TRAINER PROFILE UPDATE ===")
        print("Content-Type:", request.content_type)
        print("request.data keys:", list(request.data.keys()))
        print("request.FILES keys:", list(request.FILES.keys()))
        serializer = self.get_serializer(instance, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        print("validated_data:", serializer.validated_data)

        if "accepted_goals" in serializer.validated_data:
            instance.accepted_goals.set(serializer.validated_data.pop("accepted_goals"))
        if "accepted_levels" in serializer.validated_data:
            instance.accepted_levels.set(
                serializer.validated_data.pop("accepted_levels")
            )

        for attr, value in serializer.validated_data.items():
            setattr(instance, attr, value)
        instance.save()

        output = self.get_serializer(instance)
        return Response(output.data)


class ClientProfileViewSet(
    mixins.RetrieveModelMixin,
    mixins.UpdateModelMixin,
    viewsets.GenericViewSet,
):
    """
    Allows a client to read and update their own profile.
    Handles avatar upload (multipart) and goal/level selection.
    """

    permission_classes = [permissions.IsAuthenticated]
    serializer_class = ClientProfileSerializer
    http_method_names = ["get", "patch", "head", "options"]
    parser_classes = [
        parsers.MultiPartParser,
        parsers.FormParser,
        parsers.JSONParser,
    ]

    def get_object(self):
        user = self.request.user
        if not user.is_client:
            raise PermissionDenied("Only clients can access this endpoint.")
        return get_object_or_404(ClientProfile, user=user)

    @action(detail=False, methods=["get"], url_path="me")
    def me(self, request):
        instance = self.get_object()
        return Response(self.get_serializer(instance).data)

    @action(detail=False, methods=["patch"], url_path="me/update")
    def me_update(self, request):
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(self.get_serializer(instance).data)


# Public Viewsets
class TrainingGoalViewSet(NormalisedLookupViewSet):
    serializer_class = TrainingGoalSerializer
    queryset = TrainingGoal.objects.all()


class ExperienceLevelViewSet(NormalisedLookupViewSet):
    serializer_class = ExperienceLevelSerializer
    queryset = ExperienceLevel.objects.all()
