from django.contrib.auth.models import (
    AbstractBaseUser,
    BaseUserManager,
    PermissionsMixin,
)
from django.core.exceptions import ValidationError
from django.db import models
from django.utils.translation import gettext_lazy as get_text_value

from core.models import ApexModel


class TrainingGoal(ApexModel):
    goal_name = models.CharField(max_length=50, unique=True)

    def __str__(self) -> str:
        return self.goal_name


class ExperienceLevel(ApexModel):
    level_name = models.CharField(max_length=50, unique=True)

    def __str__(self) -> str:
        return self.level_name


class MembershipStatus(ApexModel):
    status_name = models.CharField(max_length=50, unique=True)

    class Meta:
        verbose_name_plural = "Membership Statuses"

    def __str__(self) -> str:
        return self.status_name


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
        email = self.normalize_email(email=email)

        # Create the model using the existing db connection
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self.db)

        return user

    def create_superuser(self, email, password=None, **extra_fields):
        # Base Superuser permissions
        extra_fields.setdefault("is_staff", True)
        extra_fields.setdefault("is_superuser", True)
        extra_fields.setdefault("is_active", True)

        # Check if something went wrong
        if extra_fields.get("is_staff") is not True:
            raise ValueError(
                "Superuser permissions and profile invalid." "Should be staff"
            )

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

    def save(self, *args, **kwargs):
        if self.is_trainer is True and self.is_client is True:
            raise ValidationError("A User cannot be both a trainer and a client")

        super().save(*args, **kwargs)

    def __str__(self) -> str:
        return self.email


class TrainerProfile(ApexModel):
    """
    Profile for a trainer user. Created on new user save with
    is_trainer role flag True
    """

    # Relate back to user
    user = models.OneToOneField(
        to=CustomUser, on_delete=models.CASCADE, related_name="trainer_profile"
    )

    specialisations = models.ManyToManyField(
        to=TrainingGoal, related_name="trainers", blank=True
    )

    accepted_experience_levels = models.ManyToManyField(
        to=ExperienceLevel, related_name="trainers", blank=True
    )

    # Required Trainer information (Company and Location)
    company = models.CharField(max_length=150, default="")

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
        to=CustomUser, on_delete=models.CASCADE, related_name="client_profile"
    )

    # Client data to match trainers and clients
    training_goal = models.ForeignKey(
        to=TrainingGoal,
        related_name="clients",
        blank=True,
        on_delete=models.SET_NULL,
        null=True,
    )

    experience_level = models.ForeignKey(
        to=ExperienceLevel,
        related_name="experience",
        blank=True,
        null=True,
        on_delete=models.SET_NULL,
    )


class TrainerClientMembership(ApexModel):
    """
    Tracks active membership agreements with trainers and clients
    Used for tracking programs and establishing the cofre hierarchy
    """

    trainer = models.ForeignKey(
        to=TrainerProfile, on_delete=models.CASCADE, related_name="clients"
    )

    client = models.ForeignKey(
        to=ClientProfile, on_delete=models.CASCADE, related_name="trainer"
    )

    status = models.ForeignKey(
        to=MembershipStatus,
        on_delete=models.PROTECT,
        null=True,
        related_name="memberships",
    )

    def save(self, *args, **kwargs):
        if self.status and self.status.status_name == "ACTIVE":
            active_exists = (
                TrainerClientMembership.objects.filter(
                    client=self.client, status__status_name="ACTIVE"
                )
                .exclude(id=self.id)
                .exists()
            )

            if active_exists:
                raise ValidationError("Client already has an trainer")

        super().save(*args, **kwargs)

    class Meta:
        # Ensures unique check of clients and trainers
        unique_together = ("trainer", "client")

    def __str__(self) -> str:
        return f"Trainer: {self.trainer.user.email}. Client: {self.client.user.email}"
