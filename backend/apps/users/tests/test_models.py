import pytest
from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError

from apps.users.models import (
    ClientProfile,
    CustomUser,
    ExperienceLevel,
    MembershipStatus,
    TrainerClientMembership,
    TrainerProfile,
    TrainingGoal,
)

User = get_user_model()

TEST_EMAILS = {
    "base": "test@apex.com",
    "admin": "admin@apex.com",
    "client": "client@apex.com",
    "trainer": "trainer@apex.com",
    "add_trainer": "trainer2@apex.com",
}

TEST_PASSWORD = "password123"


@pytest.mark.django_db
class TestCustomUserModel:
    def test_create_standard_user(self):
        """
        Test creating a user doesnt trigger an error without a username.
        Test creating a user with email/password works
        Test user id is a UUID
        """

        # Create the user
        user = User.objects.create_user(
            email=TEST_EMAILS["base"],
            password=TEST_PASSWORD,
            is_active=True,
        )

        # Assertions
        assert user.email == TEST_EMAILS["base"]
        assert user.check_password(TEST_PASSWORD)
        assert user.is_active is True

        # UUID check
        assert len(str(user.id)) == 36

    def test_create_super_user(self):
        """
        Test superuser permissions
        """
        admin = User.objects.create_superuser(
            email=TEST_EMAILS["admin"], password=TEST_PASSWORD, is_active=True
        )

        assert admin.is_superuser
        assert admin.is_staff

    def test_user_not_trainer_and_client(self):
        user = User.objects.create_user(
            email=TEST_EMAILS["base"],
            password=TEST_PASSWORD,
            is_active=True,
            is_client=True,
        )

        # Try check if a setting is_client and is_trainer triggers the error
        with pytest.raises(ValidationError):
            user.is_trainer = True
            user.save()


# Test Signal
@pytest.mark.django_db
class TestUserProfileSignal:
    def test_trainer_profile_auto_creation(self):
        """
        Signal should automatically create a trainer profile
        """
        user = User.objects.create(
            email=TEST_EMAILS["trainer"], password=TEST_PASSWORD, is_trainer=True
        )

        user.refresh_from_db()

        assert hasattr(user, "trainer_profile")
        assert isinstance(user.trainer_profile, TrainerProfile)

    def test_client_profile_auto_creation(self):
        """
        Signal should automatically create a client profile
        """
        user = User.objects.create(
            email=TEST_EMAILS["client"], password=TEST_PASSWORD, is_client=True
        )

        user.refresh_from_db()

        assert hasattr(user, "client_profile")
        assert isinstance(user.client_profile, ClientProfile)


# Test unique and single instance of membership
@pytest.mark.django_db
class TestMembershipLogic:
    def test_single_active_trainer_constraint(self):
        """
        Tests a client cannot have two active trainers at once.
        """

        active_status, _ = MembershipStatus.objects.get_or_create(status_name="ACTIVE")

        # Create the actors
        trainer_1 = User.objects.create(
            email=TEST_EMAILS["trainer"], password=TEST_PASSWORD, is_trainer=True
        ).trainer_profile
        trainer_2 = User.objects.create(
            email=TEST_EMAILS["add_trainer"], password=TEST_PASSWORD, is_trainer=True
        ).trainer_profile
        client = User.objects.create(
            email=TEST_EMAILS["client"], password=TEST_PASSWORD, is_client=True
        ).client_profile

        # Create the active membership
        TrainerClientMembership.objects.create(
            trainer=trainer_1, client=client, status=active_status
        )

        # Try to create a new one with a different trainer
        # Should fail
        with pytest.raises(ValidationError):
            TrainerClientMembership.objects.create(
                trainer=trainer_2, client=client, status=active_status
            )

    def test_switching_trainers(self):
        """
        Tests a client can switch trainers
        as long as they dont have an existing membership
        """

        # Create status records
        active_status, _ = MembershipStatus.objects.get_or_create(status_name="ACTIVE")
        dissolved_status, _ = MembershipStatus.objects.get_or_create(
            status_name="CLIENT_DISSOLVED"
        )

        # Set up users
        trainer_1 = User.objects.create(
            email=TEST_EMAILS["trainer"], password=TEST_PASSWORD, is_trainer=True
        ).trainer_profile

        trainer_2 = User.objects.create(
            email=TEST_EMAILS["add_trainer"], password=TEST_PASSWORD, is_trainer=True
        ).trainer_profile

        client = User.objects.create(
            email=TEST_EMAILS["client"], password=TEST_PASSWORD, is_client=True
        ).client_profile

        TrainerClientMembership.objects.create(
            trainer=trainer_1, client=client, status=dissolved_status
        )

        new_membership = TrainerClientMembership.objects.create(
            trainer=trainer_2, client=client, status=active_status
        )

        assert new_membership.id is not None
