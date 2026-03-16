from decimal import Decimal

from django.contrib.auth.models import (
    AbstractBaseUser,
    BaseUserManager,
    PermissionsMixin,
)
from django.core.exceptions import ValidationError
from django.db import models
from django.utils.translation import gettext_lazy as get_text_value

from apps.users.constants import MembershipVocabulary
from core.models import ApexModel, NormalisedLookupModel


class TrainingGoal(NormalisedLookupModel):
    rep_range_min = models.PositiveSmallIntegerField(null=True, blank=True)
    rep_range_max = models.PositiveSmallIntegerField(null=True, blank=True)

    class Meta:
        verbose_name_plural = "Training Goals"

    def clean(self):
        super().clean()

        if (self.rep_range_min is None) != (self.rep_range_max is None):
            raise ValidationError(
                "rep_range_min and rep_range_max must either both be set or both be blank."
            )

        if (
            self.rep_range_min is not None
            and self.rep_range_max is not None
            and self.rep_range_min > self.rep_range_max
        ):
            raise ValidationError(
                {"rep_range_min": "rep_range_min cannot exceed rep_range_max."}
            )


class ExperienceLevel(NormalisedLookupModel):
    progression_cap_percent = models.DecimalField(
        max_digits=4,
        decimal_places=2,
        null=True,
        blank=True,
    )

    class Meta:
        verbose_name_plural = "Experience Levels"

    def clean(self):
        super().clean()

        if self.progression_cap_percent is None:
            return

        if not (Decimal("0.00") <= self.progression_cap_percent <= Decimal("1.00")):
            raise ValidationError(
                {
                    "progression_cap_percent": (
                        "progression_cap_percent must be between 0.00 and 1.00."
                    )
                }
            )


class MembershipStatus(NormalisedLookupModel):
    class Meta:
        verbose_name_plural = "Membership Statuses"


class CustomUserManager(BaseUserManager):
    """
    Custom manager where email is the unique identifier
    for authentication instead of username
    """

    def create_user(self, email, password=None, **extra_fields):
        # Break early without email
        if not email:
            raise ValueError("The email field must be included")

        # Lowercase email domain
        email = self.normalize_email(email)

        # Create the model using the existing db connection
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)

        return user

    def create_superuser(self, email, password=None, **extra_fields):
        # Base Superuser permissions
        extra_fields.setdefault("is_staff", True)
        extra_fields.setdefault("is_superuser", True)
        extra_fields.setdefault("is_active", True)

        # Check if something went wrong
        if extra_fields.get("is_staff") is not True:
            raise ValueError("Superuser must have is_staff=True")

        if extra_fields.get("is_superuser") is not True:
            raise ValueError("Superuser must have is_superuser=True")

        return self.create_user(email=email, password=password, **extra_fields)


class CustomUser(ApexModel, AbstractBaseUser, PermissionsMixin):
    """
    Overrides base User model. Role Flags to determine trainer or client.
    Uses email as authentication instead of username.
    Defines UserManager as defined Custom Manager to override username authentication.
    """

    # Base User fields
    email = models.EmailField(get_text_value("email_address"), unique=True)
    first_name = models.CharField(max_length=150, blank=True)
    last_name = models.CharField(max_length=150, blank=True)

    # Role flags
    is_trainer = models.BooleanField(default=False)
    is_client = models.BooleanField(default=False)

    # Standard Admin fields
    is_staff = models.BooleanField(default=False)
    is_active = models.BooleanField(default=False)

    # Defines what user.objects is, set it to our custom user manager
    objects = CustomUserManager()

    # Deprecate the username field to use email
    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = ["first_name", "last_name"]

    def clean(self):
        if self.is_trainer and self.is_client:
            raise ValidationError("A User cannot be both a trainer and a client")

        return super().clean()

    def save(self, *args, **kwargs):
        self.full_clean()
        super().save(*args, **kwargs)

    def get_full_name(self):
        return f"{self.first_name} {self.last_name}".strip()

    def __str__(self) -> str:
        return self.email


class TrainerProfile(ApexModel):
    """
    Profile for a trainer user. Created on new user save with
    is_trainer role flag True
    """

    user = models.OneToOneField(
        to=CustomUser,
        on_delete=models.CASCADE,
        related_name="trainer_profile",
    )

    accepted_goals = models.ManyToManyField(
        to=TrainingGoal, related_name="trainers", blank=True
    )

    accepted_levels = models.ManyToManyField(
        to=ExperienceLevel, related_name="trainers", blank=True
    )

    # Required Trainer information (Company and Location)
    company = models.CharField(max_length=150, blank=True)

    # Optional trainer information (Website and Logo)
    website = models.URLField(max_length=150, blank=True)

    logo = models.ImageField(upload_to="trainer_company_logos/", blank=True)

    def __str__(self) -> str:
        return f"Trainer: {self.user.email}"


class ClientProfile(ApexModel):
    """
    Profile for a client user. Created on new user save with
    is_client role flag True
    """

    user = models.OneToOneField(
        to=CustomUser,
        on_delete=models.CASCADE,
        related_name="client_profile",
    )

    # Client data to match trainers and clients
    goal = models.ForeignKey(
        to=TrainingGoal,
        related_name="clients",
        blank=True,
        on_delete=models.SET_NULL,
        null=True,
    )

    level = models.ForeignKey(
        to=ExperienceLevel,
        related_name="clients",
        blank=True,
        null=True,
        on_delete=models.SET_NULL,
    )

    avatar = models.ImageField(
        upload_to="client_avatars/",
        blank=True
    )

    def __str__(self):
        return f"Client: {self.user.email}"


class TrainerClientMembership(ApexModel):
    """
    Tracks active membership agreements with trainers and clients
    Used for tracking programs and establishing the core hierarchy
    """

    # Core Data
    trainer = models.ForeignKey(
        to=TrainerProfile, on_delete=models.CASCADE, related_name="client_memberships"
    )

    client = models.ForeignKey(
        to=ClientProfile, on_delete=models.CASCADE, related_name="trainer_memberships"
    )

    status = models.ForeignKey(
        to=MembershipStatus,
        on_delete=models.PROTECT,
        related_name="memberships",
    )

    # Initiation Metadata
    requested_at = models.DateTimeField(auto_now_add=True)
    responded_at = models.DateTimeField(null=True, blank=True)
    started_at = models.DateTimeField(null=True, blank=True)
    ended_at = models.DateTimeField(null=True, blank=True)

    # Archive Metadata
    ended_by = models.ForeignKey(
        to=CustomUser,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="ended_memberships",
    )

    previous_membership = models.ForeignKey(
        to="self",
        related_name="renewals",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
    )

    is_active = models.BooleanField(default=False)

    class Meta:
        ordering = ["-updated_at"]

        # Ensures unique check of clients and trainers
        constraints = [
            models.UniqueConstraint(
                fields=["client", "trainer"],
                name="unique_active_trainer_client_membership_constraint",
                condition=models.Q(is_active=True),
            )
        ]

    def clean(self) -> None:
        if not self.trainer.user.is_trainer:
            raise ValidationError("Membership trainers must belong to a trainer user.")

        if not self.client.user.is_client:
            raise ValidationError("Membership clients must belong to a client user.")

        responded_codes = {MembershipVocabulary.ACTIVE, MembershipVocabulary.REJECTED}
        archived_codes = {
            MembershipVocabulary.DISSOLVED_BY_CLIENT,
            MembershipVocabulary.DISSOLVED_BY_TRAINER,
        }

        if self.status.code in responded_codes and not self.responded_at:
            raise ValidationError(
                "Memberships responded to must record a timestamp of action."
            )
        if self.status.code == MembershipVocabulary.ACTIVE and not self.started_at:
            raise ValidationError(
                "Active memberships must have a started at timestamp."
            )
        if self.status.code in archived_codes and not self.ended_at:
            raise ValidationError(
                "Archived memberships must have an ended at timestamp."
            )
        if self.ended_by and self.ended_by not in (self.client.user, self.trainer.user):
            raise ValidationError("Memberships can only be ended by related actors.")
        if self.status.code in archived_codes and not self.ended_by:
            raise ValidationError("Archived memberships must be related to an actor.")

        return super().clean()

    def save(self, *args, **kwargs):
        self.is_active = self.status and self.status.code == MembershipVocabulary.ACTIVE
        self.full_clean()
        super().save(*args, **kwargs)

    def __str__(self) -> str:
        return f"Trainer: {self.trainer.user.email}.\
            Client: {self.client.user.email}. Status: {self.status.code}"
