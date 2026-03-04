from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import filters, permissions, serializers
from rest_framework.exceptions import PermissionDenied
from rest_framework.viewsets import ModelViewSet, ReadOnlyModelViewSet

from .filters import TrainerClientMembershipFilter
from .models import (
    ExperienceLevel,
    MembershipStatus,
    TrainerClientMembership,
    TrainerProfile,
    TrainingGoal,
)
from .serializers import (
    ExperienceLevelSerializer,
    MembershipStatusSerializer,
    TrainerClientMembershipSerializer,
    TrainerProfileSerializer,
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

    def perform_create(self, serializer):
        user = self.request.user

        if not user.is_client:
            raise PermissionDenied(
                "Permission Denied: Only client can initiate a membership request."
            )

        pending_status = MembershipStatus.objects.get(
            status_name="PENDING_TRAINER_REVIEW"
        )

        serializer.save(client=user.client_profile, status=pending_status)

    def perform_update(self, serializer):
        user = self.request.user
        membership = self.get_object()
        new_status = serializer.validated_data.get("status")

        if not new_status:
            serializer.save()
            return

        status_name = new_status.status_name
        current_status = membership.status.status_name

        # Trainer Path
        if user.is_trainer:

            # Only allow change of memberships of my clients
            if membership.trainer != user.trainer_profile:
                raise PermissionDenied("Not your client")

            # Can only accept or reject a pending membership
            if current_status == "PENDING_TRAINER_REVIEW":
                if status_name not in ["ACTIVE", "REJECTED"]:
                    raise serializers.ValidationError(
                        "You can only Accept or Reject pending requests."
                    )

            # Can only dissolve an active membership
            elif current_status == "ACTIVE":
                if status_name != "TRAINER_DISSOLVED":
                    raise serializers.ValidationError(
                        "You can only dissolve active memberships."
                    )

            # Something else went wrong
            else:
                raise serializers.ValidationError(
                    "Cannot change status of this membership."
                )

        # Client Path
        elif user.is_client:

            # Ensure its their membership
            if membership.client != user.client_profile:
                raise PermissionDenied("Not your trainer")

            # Client can cancel pending requests
            if current_status == "PENDING_TRAINER_REVIEW":
                if status_name != "CLIENT_DISSOLVED":
                    raise serializers.ValidationError(
                        "You can only cancel pending requests."
                    )

            # Clients can only dissolved active requests
            elif current_status == "ACTIVE":
                if status_name != "CLIENT_DISSOLVED":
                    raise serializers.ValidationError(
                        "You can only dissolve active memberships."
                    )

            # Something else went wrong
            else:
                raise serializers.ValidationError(
                    "Cannot change status of this membership."
                )

        # All checks passed. Safe to save.
        serializer.save()


class TrainerMatchingViewset(ReadOnlyModelViewSet):
    serializer_class = TrainerProfileSerializer
    permission_classes = [permissions.IsAuthenticated]

    filter_backends = [DjangoFilterBackend, filters.SearchFilter]
    search_fields = ["user__email", "company", "website"]

    def get_queryset(self):
        # Trainers cant search for other trainers
        user = self.request.user

        queryset = TrainerProfile.objects.select_related("user").prefetch_related(
            "specialisations",
            "accepted_experience_levels",
        )

        if user.is_trainer:
            return TrainerProfile.objects.none()

        elif user.is_client:
            profile = user.client_profile
            return queryset.filter(
                specialisations=profile.training_goal,
                accepted_experience_levels=profile.experience_level,
            ).distinct()

        return TrainerProfile.objects.none()


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
