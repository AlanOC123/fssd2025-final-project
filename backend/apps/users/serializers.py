from dj_rest_auth.registration.serializers import RegisterSerializer
from dj_rest_auth.serializers import PasswordResetSerializer
from django.conf import settings
from django.contrib.auth import get_user_model
from django.contrib.auth.password_validation import validate_password
from django.contrib.auth.tokens import default_token_generator
from django.core.exceptions import ValidationError as DjangoValidationError
from django.utils.encoding import force_bytes, force_str
from django.utils.http import urlsafe_base64_decode, urlsafe_base64_encode
from rest_framework import serializers

from core.serializers import ApexSerializer, LabelLookupSerializer

from .models import (
    ClientProfile,
    ExperienceLevel,
    TrainerClientMembership,
    TrainerProfile,
    TrainingGoal,
)

User = get_user_model()


class UserIdSerializer(serializers.ModelSerializer):
    """Simple serializer to expose only the user's primary key."""

    class Meta:
        model = User
        fields = ["id"]
        read_only_fields = fields


class TrainingGoalSerializer(LabelLookupSerializer):
    """Serializer for TrainingGoal using label-based lookup logic."""

    class Meta(LabelLookupSerializer.Meta):
        model = TrainingGoal


class ExperienceLevelSerializer(LabelLookupSerializer):
    """Serializer for ExperienceLevel using label-based lookup logic."""

    class Meta(LabelLookupSerializer.Meta):
        model = ExperienceLevel


class ClientProfileSerializer(ApexSerializer):
    """Serializer for ClientProfile including goal and experience details.

    Handles read-only nested representations for goals and levels while
    allowing updates via primary key fields.
    """

    goal = TrainingGoalSerializer(read_only=True)
    level = ExperienceLevelSerializer(read_only=True)

    goal_id = serializers.PrimaryKeyRelatedField(
        queryset=TrainingGoal.objects.all(),
        source="goal",
        write_only=True,
        required=False,
        allow_null=True,
    )

    level_id = serializers.PrimaryKeyRelatedField(
        queryset=ExperienceLevel.objects.all(),
        source="level",
        write_only=True,
        required=False,
        allow_null=True,
    )

    class Meta(ApexSerializer.Meta):
        model = ClientProfile
        fields = ApexSerializer.Meta.fields + [
            "goal",
            "level",
            "goal_id",
            "level_id",
            "avatar",
        ]
        read_only_fields = ApexSerializer.Meta.read_only_fields + ["goal", "level"]


class TrainerProfileSerializer(ApexSerializer):
    """Serializer for TrainerProfile with support for many-to-many relationships.

    Exposes accepted goals and levels as nested objects for reads and
    primary key lists for writes.
    """

    accepted_goals = TrainingGoalSerializer(many=True, read_only=True)
    accepted_levels = ExperienceLevelSerializer(many=True, read_only=True)

    accepted_goal_ids = serializers.PrimaryKeyRelatedField(
        queryset=TrainingGoal.objects.all(),
        source="accepted_goals",
        write_only=True,
        required=False,
        many=True,
    )

    accepted_level_ids = serializers.PrimaryKeyRelatedField(
        queryset=ExperienceLevel.objects.all(),
        source="accepted_levels",
        write_only=True,
        required=False,
        many=True,
    )

    class Meta(ApexSerializer.Meta):
        model = TrainerProfile
        fields = ApexSerializer.Meta.fields + [
            "accepted_goals",
            "accepted_levels",
            "accepted_goal_ids",
            "accepted_level_ids",
            "company",
            "website",
            "logo",
        ]

        read_only_fields = ApexSerializer.Meta.read_only_fields + [
            "accepted_goals",
            "accepted_levels",
        ]


class TrainerMatchingSerializer(ApexSerializer):
    """Specialized serializer for matching clients with trainers.

    Includes basic user identification and trainer-specific capabilities.
    """

    first_name = serializers.CharField(source="user.first_name", read_only=True)
    last_name = serializers.CharField(source="user.last_name", read_only=True)
    email = serializers.CharField(source="user.email", read_only=True)

    accepted_goals = TrainingGoalSerializer(many=True, read_only=True)
    accepted_levels = ExperienceLevelSerializer(many=True, read_only=True)

    class Meta(ApexSerializer.Meta):
        model = TrainerProfile
        fields = ApexSerializer.Meta.fields + [
            "first_name",
            "last_name",
            "email",
            "accepted_goals",
            "accepted_levels",
        ]

        read_only_fields = ApexSerializer.Meta.fields + fields


class CustomUserSerializer(ApexSerializer):
    """Serializer for CustomUser providing derived profile and role data.

    Calculates roles and dynamically fetches the appropriate profile
    type based on user flags.
    """

    profile = serializers.SerializerMethodField()
    role = serializers.SerializerMethodField()
    full_name = serializers.SerializerMethodField()

    class Meta(ApexSerializer.Meta):
        model = User
        fields = ApexSerializer.Meta.fields + [
            "email",
            "first_name",
            "last_name",
            "full_name",
            "is_trainer",
            "is_client",
            "role",
            "profile",
        ]

    def get_full_name(self, obj):
        """Retrieves user's full name."""
        return obj.get_full_name()

    def get_role(self, obj):
        """Determines user's role based on flags.

        Returns:
            str: One of 'admin', 'trainer', 'client', or 'unknown'.
        """
        if obj.is_superuser:
            return "admin"
        if obj.is_trainer:
            return "trainer"
        if obj.is_client:
            return "client"
        return "unknown"

    def get_profile(self, obj):
        """Returns serialized profile data based on user type.

        Returns:
            dict: Serialized profile data or None if no profile exists.
        """
        if obj.is_client and hasattr(obj, "client_profile"):
            return ClientProfileSerializer(obj.client_profile).data

        if obj.is_trainer and hasattr(obj, "trainer_profile"):
            return TrainerProfileSerializer(obj.trainer_profile).data

        return None


class ApexPasswordResetSerializer(PasswordResetSerializer):
    """Custom serializer to send password reset emails via frontend routes."""

    def save(self):
        """Generates reset tokens and sends the email to the user."""
        email = self.data.get("email", "")

        try:
            user = User.objects.get(email__iexact=email, is_active=True)
        except User.DoesNotExist:
            return

        uid = urlsafe_base64_encode(force_bytes(user.pk))
        token = default_token_generator.make_token(user)
        reset_url = f"{settings.PASSWORD_RESET_LINK}?uid={uid}&token={token}"

        if settings.IS_PROD:
            from anymail.message import AnymailMessage

            msg = AnymailMessage(
                subject="Reset your Apex password",
                body=(
                    f"Hi {user.get_full_name() or user.email},\n\n"
                    f"Click the link below to reset your password:\n\n"
                    f"{reset_url}\n\n"
                    f"If you didn't request this, ignore this email.\n"
                ),
                to=[user.email],
                from_email=settings.DEFAULT_FROM_EMAIL,
            )
            msg.send()
        else:
            from django.core.mail import send_mail

            send_mail(
                subject="Reset your Apex password",
                message=(
                    f"Hi {user.get_full_name() or user.email},\n\n"
                    f"Click the link below to reset your password:\n\n"
                    f"{reset_url}\n\n"
                    f"If you didn't request this, ignore this email.\n"
                ),
                from_email=settings.DEFAULT_FROM_EMAIL,
                recipient_list=[user.email],
                fail_silently=False,
            )


class ApexPasswordResetConfirmSerializer(serializers.Serializer):
    """Handles verification and setting of new passwords using UUIDs.

    Decodes the base64 UID and checks the token validity against the user.
    """

    uid = serializers.CharField()
    token = serializers.CharField()
    new_password1 = serializers.CharField(max_length=128, write_only=True)
    new_password2 = serializers.CharField(max_length=128, write_only=True)

    def validate(self, attrs):
        """Validates the reset token, UID, and password consistency.

        Returns:
            dict: Validated attributes.

        Raises:
            ValidationError: If token/UID is invalid or passwords mismatch.
        """
        try:
            uid = force_str(urlsafe_base64_decode(attrs["uid"]))
            self.user = User.objects.get(pk=uid)
        except (TypeError, ValueError, OverflowError, User.DoesNotExist):
            raise serializers.ValidationError({"uid": "Invalid reset link."})

        if not default_token_generator.check_token(self.user, attrs["token"]):
            raise serializers.ValidationError(
                {"token": "Invalid or expired reset link."}
            )

        if attrs["new_password1"] != attrs["new_password2"]:
            raise serializers.ValidationError(
                {"new_password2": "Passwords do not match."}
            )

        try:
            validate_password(attrs["new_password1"], self.user)
        except DjangoValidationError as e:
            raise serializers.ValidationError({"new_password1": list(e.messages)})

        return attrs

    def save(self):
        """Applies the new password to the user."""
        self.user.set_password(self.validated_data["new_password1"])
        self.user.save()
        return self.user


class CustomRegisterSerializer(RegisterSerializer):
    """Registration serializer supporting custom roles and profile creation.

    Directly assigns trainer/client flags and ensures profile existence.
    """

    username = None
    first_name = serializers.CharField(required=True, max_length=150)
    last_name = serializers.CharField(required=True, max_length=150)
    role = serializers.ChoiceField(choices=["trainer", "client"], write_only=True)

    def get_cleaned_data(self):
        """Prepares initial data, removing unnecessary username field."""
        data = super().get_cleaned_data()
        data.pop("username", None)
        data["first_name"] = self.validated_data.get("first_name", "")
        data["last_name"] = self.validated_data.get("last_name", "")
        return data

    def save(self, request):
        """Saves the user and triggers manual profile generation.

        Args:
            request: The registration request object.

        Returns:
            CustomUser: The newly created user instance.
        """
        user = super().save(request)

        role = self.validated_data.get("role", "")
        user.is_trainer = role == "trainer"
        user.is_client = role == "client"

        User.objects.filter(pk=user.pk).update(
            is_trainer=user.is_trainer,
            is_client=user.is_client,
        )

        if user.is_trainer and not hasattr(user, "trainer_profile"):
            from apps.users.models import TrainerProfile

            TrainerProfile.objects.get_or_create(user=user)
        elif user.is_client and not hasattr(user, "client_profile"):
            from apps.users.models import ClientProfile

            ClientProfile.objects.get_or_create(user=user)

        return user


class TrainerClientMembershipSerializer(ApexSerializer):
    """Serializer for tracking memberships between trainers and clients."""

    trainer_name = serializers.SerializerMethodField()
    client_name = serializers.SerializerMethodField()

    status_code = serializers.CharField(source="status.code", read_only=True)
    status_label = serializers.CharField(source="status.label", read_only=True)

    trainer_id = serializers.PrimaryKeyRelatedField(
        queryset=TrainerProfile.objects.all(),
        source="trainer",
        required=False,
        write_only=True,
    )

    status_id = serializers.UUIDField(source="status.id", read_only=True)

    class Meta(ApexSerializer.Meta):
        model = TrainerClientMembership

        fields = ApexSerializer.Meta.fields + [
            "trainer_name",
            "client_name",
            "status_code",
            "status_label",
            "status_id",
            "trainer_id",
            "requested_at",
            "responded_at",
            "started_at",
            "ended_at",
        ]

        read_only_fields = ApexSerializer.Meta.read_only_fields + [
            "trainer_name",
            "client_name",
            "status_id",
            "status_code",
            "status_label",
            "requested_at",
            "responded_at",
            "started_at",
            "ended_at",
        ]

    def get_trainer_name(self, obj):
        """Retrieves the full name or email of the trainer."""
        name = obj.trainer.user.get_full_name()
        return name if name else obj.trainer.user.email

    def get_client_name(self, obj):
        """Retrieves the full name or email of the client."""
        name = obj.client.user.get_full_name()
        return name if name else obj.client.user.email


class MembershipRequestSerializer(serializers.Serializer):
    """Simplified serializer for initiating membership requests."""

    trainer_id = serializers.PrimaryKeyRelatedField(
        queryset=TrainerProfile.objects.all(),
    )


class TrainerProfileWriteSerializer(ApexSerializer):
    """Serializer allowing trainers to manage their own profile details."""

    accepted_goal_ids = serializers.PrimaryKeyRelatedField(
        queryset=TrainingGoal.objects.all(),
        source="accepted_goals",
        write_only=True,
        required=False,
        many=True,
    )

    accepted_level_ids = serializers.PrimaryKeyRelatedField(
        queryset=ExperienceLevel.objects.all(),
        source="accepted_levels",
        write_only=True,
        required=False,
        many=True,
    )

    accepted_goals = TrainingGoalSerializer(many=True, read_only=True)
    accepted_levels = ExperienceLevelSerializer(many=True, read_only=True)

    class Meta(ApexSerializer.Meta):
        model = TrainerProfile
        fields = ApexSerializer.Meta.fields + [
            "accepted_goals",
            "accepted_levels",
            "accepted_goal_ids",
            "accepted_level_ids",
            "company",
            "website",
            "logo",
        ]
        read_only_fields = ApexSerializer.Meta.read_only_fields + [
            "accepted_goals",
            "accepted_levels",
        ]
