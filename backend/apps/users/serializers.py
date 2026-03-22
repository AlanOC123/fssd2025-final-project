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
    class Meta:
        model = User
        fields = ["id"]
        read_only_fields = fields


class TrainingGoalSerializer(LabelLookupSerializer):

    class Meta(LabelLookupSerializer.Meta):
        model = TrainingGoal


class ExperienceLevelSerializer(LabelLookupSerializer):
    class Meta(LabelLookupSerializer.Meta):
        model = ExperienceLevel


class ClientProfileSerializer(ApexSerializer):
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
    """Used for matching trainers with clients"""

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
        return obj.get_full_name()

    def get_role(self, obj):
        if obj.is_superuser:
            return "admin"
        if obj.is_trainer:
            return "trainer"
        if obj.is_client:
            return "client"
        return "unknown"

    def get_profile(self, obj):
        if obj.is_client and hasattr(obj, "client_profile"):
            return ClientProfileSerializer(obj.client_profile).data

        if obj.is_trainer and hasattr(obj, "trainer_profile"):
            return TrainerProfileSerializer(obj.trainer_profile).data

        return None


class ApexPasswordResetSerializer(PasswordResetSerializer):
    """
    Bypasses reverse('password_reset_confirm') by finding the user directly
    and sending a plain email with our frontend reset URL.
    """

    def save(self):
        email = self.data.get("email", "")

        # Find active users with this email
        try:
            user = User.objects.get(email__iexact=email, is_active=True)
        except User.DoesNotExist:
            # Don't reveal whether the email exists
            return

        uid = urlsafe_base64_encode(force_bytes(user.pk))
        token = default_token_generator.make_token(user)
        reset_url = f"{settings.PASSWORD_RESET_LINK}?uid={uid}&token={token}"

        print(reset_url)

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
    """
    Handles password reset confirm for UUID primary key users.
    Django's default confirm serializer expects integer PKs — this one
    decodes the base64 uid back to a UUID string.
    """

    uid = serializers.CharField()
    token = serializers.CharField()
    new_password1 = serializers.CharField(max_length=128, write_only=True)
    new_password2 = serializers.CharField(max_length=128, write_only=True)

    def validate(self, attrs):
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
        self.user.set_password(self.validated_data["new_password1"])
        self.user.save()
        return self.user


class CustomRegisterSerializer(RegisterSerializer):
    username = None
    first_name = serializers.CharField(required=True, max_length=150)
    last_name = serializers.CharField(required=True, max_length=150)
    role = serializers.ChoiceField(choices=["trainer", "client"], write_only=True)

    def get_cleaned_data(self):
        data = super().get_cleaned_data()
        data.pop("username", None)
        data["first_name"] = self.validated_data.get("first_name", "")
        data["last_name"] = self.validated_data.get("last_name", "")
        return data

    def save(self, request):
        # Call the parent save() which creates the user via allauth
        user = super().save(request)

        # Set role flags directly after creation — get_cleaned_data can't
        # reliably pass is_trainer/is_client through allauth's save_user()
        role = self.validated_data.get("role", "")
        user.is_trainer = role == "trainer"
        user.is_client = role == "client"

        # Use queryset update to bypass full_clean() and avoid the double-save
        # unique constraint issue we already fixed in models.py
        User.objects.filter(pk=user.pk).update(
            is_trainer=user.is_trainer,
            is_client=user.is_client,
        )

        # Manually trigger profile creation since the signal already fired
        # before we set the role flags
        if user.is_trainer and not hasattr(user, "trainer_profile"):
            from apps.users.models import TrainerProfile

            TrainerProfile.objects.get_or_create(user=user)
        elif user.is_client and not hasattr(user, "client_profile"):
            from apps.users.models import ClientProfile

            ClientProfile.objects.get_or_create(user=user)

        return user


class TrainerClientMembershipSerializer(ApexSerializer):
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
        name = obj.trainer.user.get_full_name()
        return name if name else obj.trainer.user.email

    def get_client_name(self, obj):
        name = obj.client.user.get_full_name()
        return name if name else obj.client.user.email


class MembershipRequestSerializer(serializers.Serializer):
    trainer_id = serializers.PrimaryKeyRelatedField(
        queryset=TrainerProfile.objects.all(),
    )


class TrainerProfileWriteSerializer(ApexSerializer):
    """Used by the trainer to update their own profile"""

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
