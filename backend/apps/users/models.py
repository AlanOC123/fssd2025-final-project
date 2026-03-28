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
    """Model representing a training objective with associated rep ranges.

    Attributes:
        rep_range_min: Minimum number of repetitions for the goal.
        rep_range_max: Maximum number of repetitions for the goal.
    """

    rep_range_min = models.PositiveSmallIntegerField(null=True, blank=True)
    rep_range_max = models.PositiveSmallIntegerField(null=True, blank=True)

    class Meta:
        verbose_name_plural = "Training Goals"

    def clean(self):
        """Validates that rep ranges are logically consistent.

        Raises:
            ValidationError: If only one rep range boundary is set, or if min
                exceeds max.
        """
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
    """Model representing the training experience level of a user.

    Attributes:
        progression_cap_percent: A decimal representing a cap on progression logic.
    """

    progression_cap_percent = models.DecimalField(
        max_digits=4,
        decimal_places=2,
        null=True,
        blank=True,
    )

    class Meta:
        verbose_name_plural = "Experience Levels"

    def clean(self):
        """Validates that the progression cap is within the 0.00 to 1.00 range.

        Raises:
            ValidationError: If progression_cap_percent is outside allowed bounds.
        """
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
    """Model representing the status of a trainer-client relationship."""

    class Meta:
        verbose_name_plural = "Membership Statuses"


class CustomUserManager(BaseUserManager):
    """Custom manager for CustomUser where email is the unique identifier."""

    def create_user(self, email, password=None, **extra_fields):
        """Creates and saves a User with the given email and password.

        Args:
            email: User's email address.
            password: User's password.
            **extra_fields: Additional fields for the user model.

        Returns:
            CustomUser: The created user instance.

        Raises:
            ValueError: If the email field is not provided.
        """
        if not email:
            raise ValueError("The email field must be included")

        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)

        return user

    def create_superuser(self, email, password=None, **extra_fields):
        """Creates and saves a superuser with the given email and password.

        Args:
            email: User's email address.
            password: User's password.
            **extra_fields: Additional fields for the user model.

        Returns:
            CustomUser: The created superuser instance.

        Raises:
            ValueError: If staff or superuser flags are not set to True.
        """
        extra_fields.setdefault("is_staff", True)
        extra_fields.setdefault("is_superuser", True)
        extra_fields.setdefault("is_active", True)

        if extra_fields.get("is_staff") is not True:
            raise ValueError("Superuser must have is_staff=True")

        if extra_fields.get("is_superuser") is not True:
            raise ValueError("Superuser must have is_superuser=True")

        return self.create_user(email=email, password=password, **extra_fields)


class CustomUser(ApexModel, AbstractBaseUser, PermissionsMixin):
    """Custom user model using email for authentication.

    Attributes:
        email: Unique identifier for the user.
        first_name: User's first name.
        last_name: User's last name.
        is_trainer: Flag indicating if the user is a trainer.
        is_client: Flag indicating if the user is a client.
        is_staff: Flag for administrative access.
        is_active: Flag for account activity.
    """

    email = models.EmailField(get_text_value("email_address"), unique=True)
    first_name = models.CharField(max_length=150, blank=True)
    last_name = models.CharField(max_length=150, blank=True)

    is_trainer = models.BooleanField(default=False)
    is_client = models.BooleanField(default=False)

    is_staff = models.BooleanField(default=False)
    is_active = models.BooleanField(default=False)

    objects = CustomUserManager()

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = ["first_name", "last_name"]

    def clean(self):
        """Validates that a user does not possess conflicting roles.

        Raises:
            ValidationError: If the user is marked as both a trainer and a client.
        """
        if self.is_trainer and self.is_client:
            raise ValidationError("A User cannot be both a trainer and a client")

        return super().clean()

    def save(self, *args, **kwargs):
        """Performs full validation before saving the user instance."""
        exclude = []
        if self.pk:
            exclude.append("email")
        self.full_clean(exclude=exclude)
        super().save(*args, **kwargs)

    def get_full_name(self):
        """Returns the user's first and last name combined.

        Returns:
            str: The full name of the user.
        """
        return f"{self.first_name} {self.last_name}".strip()

    def __str__(self) -> str:
        return self.email


class TrainerProfile(ApexModel):
    """Profile model for trainers.

    Attributes:
        user: One-to-one relationship with CustomUser.
        accepted_goals: Goals the trainer is willing to work with.
        accepted_levels: Experience levels the trainer accommodates.
        company: Trainer's company name.
        website: Trainer's professional website.
        logo: Trainer's company logo.
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

    company = models.CharField(max_length=150, blank=True)
    website = models.URLField(max_length=150, blank=True)
    logo = models.ImageField(upload_to="trainer_company_logos/", blank=True)

    def __str__(self) -> str:
        return f"Trainer: {self.user.email}"


class ClientProfile(ApexModel):
    """Profile model for clients.

    Attributes:
        user: One-to-one relationship with CustomUser.
        goal: The client's current training goal.
        level: The client's current experience level.
        avatar: Client's profile picture.
    """

    user = models.OneToOneField(
        to=CustomUser,
        on_delete=models.CASCADE,
        related_name="client_profile",
    )

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

    avatar = models.ImageField(upload_to="client_avatars/", blank=True)

    def __str__(self):
        return f"Client: {self.user.email}"


class TrainerClientMembership(ApexModel):
    """Tracks agreements and status between trainers and clients.

    Attributes:
        trainer: The trainer involved in the membership.
        client: The client involved in the membership.
        status: The current status of the membership.
        requested_at: Timestamp of the initial request.
        responded_at: Timestamp of when the request was accepted/rejected.
        started_at: Timestamp of when the active phase began.
        ended_at: Timestamp of when the membership was terminated.
        ended_by: User who terminated the membership.
        previous_membership: Reference to a previous renewal instance.
        is_active: Boolean flag derived from status.
    """

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

    requested_at = models.DateTimeField(auto_now_add=True)
    responded_at = models.DateTimeField(null=True, blank=True)
    started_at = models.DateTimeField(null=True, blank=True)
    ended_at = models.DateTimeField(null=True, blank=True)

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
        constraints = [
            models.UniqueConstraint(
                fields=["client", "trainer"],
                name="unique_active_trainer_client_membership_constraint",
                condition=models.Q(is_active=True),
            )
        ]

    def clean(self) -> None:
        """Validates membership integrity and state transition timestamps.

        Raises:
            ValidationError: If profile roles are incorrect, timestamps are
                missing for relevant statuses, or the ending actor is unrelated.
        """
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
        """Sets active flag based on status and performs full validation."""
        self.is_active = self.status and self.status.code == MembershipVocabulary.ACTIVE
        self.full_clean()
        super().save(*args, **kwargs)

    def __str__(self) -> str:
        return f"Trainer: {self.trainer.user.email}. Client: {self.client.user.email}. Status: {self.status.code}"
