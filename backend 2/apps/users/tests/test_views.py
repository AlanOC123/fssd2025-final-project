import pytest
from django.contrib.auth import get_user_model
from model_bakery import baker
from rest_framework import status
from rest_framework.test import APIClient

from apps.users.models import (
    ClientProfile,
    ExperienceLevel,
    MembershipStatus,
    TrainerClientMembership,
    TrainerProfile,
    TrainingGoal,
)

User = get_user_model()


@pytest.fixture
def api_client():
    """Make an API Client available for use throughout testing"""
    return APIClient()


@pytest.mark.django_db
class TestTrainerClientMembershipViewset:

    @pytest.fixture(autouse=True)
    def setup_data(self):
        """
        World State:
        - Trainer A has 1 active membership (mem_a)
        - Trainer B has 1 active membership (mem_b)
        - Client User has 1 active membership (mem_client)
        """

        # Membership Status
        self.active_status = baker.make(MembershipStatus, status_name="ACTIVE")
        self.inactive_status = baker.make(
            MembershipStatus, status_name="CLIENT_DISSOLVED"
        )

        # Actors
        self.trainer_a = baker.make(User, is_trainer=True)
        self.trainer_b = baker.make(User, is_trainer=True)
        self.client = baker.make(User, is_client=True)

        # Data
        self.mem_a = baker.make(
            TrainerClientMembership, trainer=self.trainer_a.trainer_profile
        )
        self.mem_b = baker.make(
            TrainerClientMembership, trainer=self.trainer_b.trainer_profile
        )

        self.mem_client = baker.make(
            TrainerClientMembership, client=self.client.client_profile
        )

    def test_isolation(self, api_client):
        """Trainer A should ONLY see mem_a"""

        # Force an authenticated state
        api_client.force_authenticate(user=self.trainer_a)

        # Get the response (self.request.user should be trainer A)
        response = api_client.get("/api/v1/users/trainer-client-memberships/")

        # Assertions
        assert response.status_code == status.HTTP_200_OK
        assert len(response.data) > 0
        assert response.data[0]["id"] == str(self.mem_a.id)
        assert response.data[0]["id"] != str(self.mem_b.id)

    def test_client_access(self, api_client):
        """Client should only see their memberships"""

        api_client.force_authenticate(user=self.client)
        response = api_client.get("/api/v1/users/trainer-client-memberships/")

        # Assertions
        assert response.status_code == status.HTTP_200_OK
        assert len(response.data) > 0
        assert response.data[0]["id"] == str(self.mem_client.id)
        assert response.data[0]["id"] != str(self.mem_a.id)
        assert response.data[0]["id"] != str(self.mem_b.id)

    def test_unauthenticated_user(self, api_client):
        """Tests an anonymous users get an empty response"""

        response = api_client.get("/api/v1/users/trainer-client-memberships/")

        # Assertions
        assert response.status_code == status.HTTP_401_UNAUTHORIZED


@pytest.mark.django_db
class TestTrainerMatchingViewset:

    @pytest.fixture(autouse=True)
    def setup_reference_data(self):
        """
        World State:
        - Goals: Strength, Muscle Mass
        - Levels: Beginner, Pro
        - Client: Seek Strength + Beginner
        - Trainer A (Match): Has Strength + Beginner
        - Trainer B (Mismatch Goal): Has Muscle Mass + Beginner
        - Trainer C (Mismatch Level): Has Strength + Pro
        """

        # Goals
        self.strength_goal = baker.make(TrainingGoal, goal_name="Strength")
        self.muscle_mass_goal = baker.make(TrainingGoal, goal_name="Muscle Mass")

        # Levels
        self.beginner_lvl = baker.make(ExperienceLevel, level_name="Beginner")
        self.advanced_lvl = baker.make(ExperienceLevel, level_name="Advanced")

        # 2. Client
        self.client_user = baker.make(User, is_client=True)

        # Save the profile preferences
        self.client_user.client_profile.training_goal = self.strength_goal
        self.client_user.client_profile.experience_level = self.beginner_lvl
        self.client_user.client_profile.save()

        # Trainer A (The Perfect Match)
        self.trainer_a = baker.make(
            User,
            is_trainer=True,
            first_name="Alice",
            last_name="Smith",
            email="alice.smith@apex.com",
        )

        p_a = self.trainer_a.trainer_profile
        p_a.specialisations.add(self.strength_goal)
        p_a.accepted_experience_levels.add(self.beginner_lvl)

        # Trainer B (Wrong Goal)
        self.trainer_b = baker.make(User, is_trainer=True)
        p_b = self.trainer_b.trainer_profile
        p_b.specialisations.add(self.muscle_mass_goal)
        p_b.accepted_experience_levels.add(self.beginner_lvl)

        # Trainer C (Wrong Level)
        self.trainer_c = baker.make(User, is_trainer=True)
        p_c = self.trainer_c.trainer_profile
        p_c.specialisations.add(self.strength_goal)
        p_c.accepted_experience_levels.add(self.advanced_lvl)

    def test_matching_logic(self, api_client):
        """Tests the matching logic of a client to relevant trainers"""

        api_client.force_authenticate(user=self.client_user)

        response = api_client.get("/api/v1/users/find-trainers/")

        assert response.status_code == status.HTTP_200_OK

        # Should get back a list of profiles
        returned_ids = [item["id"] for item in response.data]

        # Should be present
        assert str(self.trainer_a.trainer_profile.id) in returned_ids

        # Shouldnt be present
        assert str(self.trainer_b.trainer_profile.id) not in returned_ids
        assert str(self.trainer_c.trainer_profile.id) not in returned_ids

    def test_serializer_fields(self, api_client):
        api_client.force_authenticate(user=self.client_user)

        response = api_client.get("/api/v1/users/find-trainers/")

        match = response.data[0]

        assert match["first_name"] == "Alice"
        assert match["last_name"] == "Smith"
        assert match["email"] == "alice.smith@apex.com"
        assert "goal_name" in match["specialisations"][0]

    def test_trainers_see_empty_list(self, api_client):
        """Trainers shouldnt be able to see other trainers"""

        api_client.force_authenticate(user=self.trainer_a)

        response = api_client.get("/api/v1/users/find-trainers/")

        assert response.status_code == status.HTTP_200_OK
        assert len(response.data) == 0

    def test_unauthenticated_user_access(self, api_client):
        """Allow anonymous users no access"""

        response = api_client.get("/api/v1/users/find-trainers/")
        assert response.status_code == status.HTTP_401_UNAUTHORIZED


@pytest.mark.django_db
class TestPublicReferenceViews:

    @pytest.fixture(autouse=True)
    def setup_reference_data(self):
        """
        World State:
        - 3 Training Goals exist
        - 2 Experience Levels exist
        """
        self.goals = baker.make(TrainingGoal, _quantity=3)
        self.levels = baker.make(ExperienceLevel, _quantity=2)

    def test_training_goals_are_public(self, api_client):
        """Tests Training Goals can be accessed by anyone"""
        response = api_client.get("/api/v1/users/training-goals/")

        assert response.status_code == status.HTTP_200_OK
        assert len(response.data) == 3
        assert response.data[0]["id"] in [str(g.id) for g in self.goals]

    def test_experience_level_are_public(self, api_client):
        """Tests Experience Levels can be accessed by anyone"""
        response = api_client.get("/api/v1/users/experience-levels/")

        assert response.status_code == status.HTTP_200_OK
        assert len(response.data) == 2
        assert response.data[0]["id"] in [str(lvl.id) for lvl in self.levels]
