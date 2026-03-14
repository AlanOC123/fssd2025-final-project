import pytest
from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from model_bakery import baker

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

        # Create the user as a trainer
        user = baker.make(User, is_trainer=True)

        # Assert the signal works
        assert hasattr(user, "trainer_profile")

    def test_client_profile_auto_creation(self):
        """
        Signal should automatically create a client profile
        """
        user = baker.make(User, is_client=True)

        assert hasattr(user, "client_profile")


# Test unique and single instance of membership
@pytest.mark.django_db
class TestMembershipLogic:

    @pytest.fixture(autouse=True)
    def setup_data(self):
        """Sets up core test data"""

        # Create statuses
        self.active_status = baker.make(MembershipStatus, status_name="ACTIVE")
        self.dissolved_status = baker.make(
            MembershipStatus, status_name="CLIENT_DISSOLVED"
        )

        # Reusable client profile
        self.client_profile = baker.make(ClientProfile)

    def test_switching_trainers(self):
        """
        Tests a client can switch trainers
        as long as they dont have an existing membership
        """

        # Create first membership (inactive)
        baker.make(
            TrainerClientMembership,
            client=self.client_profile,
            status=self.dissolved_status,
        )

        # Create second membership (active)
        new_membership = baker.make(
            TrainerClientMembership,
            client=self.client_profile,
            status=self.active_status,
        )

        # Ensure creation of new membership
        assert new_membership.id is not None
