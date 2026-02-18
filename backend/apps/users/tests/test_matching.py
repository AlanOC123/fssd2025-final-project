import pytest
from django.contrib.auth import get_user_model

from apps.users.models import (
    ClientProfile,
    CustomUser,
    ExperienceLevel,
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
    "add_trainer2": "trainer3@apex.com",
}

TEST_PASSWORD = "password123"

GOAL_STRENGTH = "Strength"
GOAL_MUSCLE_MASS = "Muscle Mass"

LEVEL_BEGIN = "Beginner"
LEVEL_INTER = "Intermediate"


@pytest.mark.django_db
class TestMatchingConstraints:

    def setup_method(self):
        # Create look up data
        self.goal_strength, _ = TrainingGoal.objects.get_or_create(
            goal_name=GOAL_STRENGTH
        )
        self.goal_muscle_mass, _ = TrainingGoal.objects.get_or_create(
            goal_name=GOAL_MUSCLE_MASS
        )

        self.level_begin, _ = ExperienceLevel.objects.get_or_create(
            level_name=LEVEL_BEGIN
        )
        self.level_inter, _ = ExperienceLevel.objects.get_or_create(
            level_name=LEVEL_INTER
        )

    def test_client_constraints_single_selection(self):
        """
        Tests if a user can only add exactly 1 goal and 1 level
        """

        user = User.objects.create(
            email=TEST_EMAILS["base"], password=TEST_PASSWORD, is_client=True
        )

        profile = user.client_profile

        # Set initial values
        profile.training_goal = self.goal_strength
        profile.experience_level = self.level_begin
        profile.save()

        # Verify
        assert profile.training_goal == self.goal_strength
        assert profile.experience_level == self.level_begin

        # Try update
        profile.training_goal = self.goal_muscle_mass
        profile.save()

        # Verify it updated not added on top
        profile.refresh_from_db()
        assert profile.training_goal == self.goal_muscle_mass
        assert profile.training_goal != self.goal_strength

    def test_trainer_constraints_many_selections(self):
        user = User.objects.create(
            email=TEST_EMAILS["trainer"], password=TEST_PASSWORD, is_trainer=True
        )

        profile = user.trainer_profile

        profile.specialisations.add(self.goal_strength, self.goal_muscle_mass)

        profile.accepted_experience_levels.add(self.level_begin, self.level_inter)

        profile.save()

        assert profile.specialisations.count() == 2
        assert profile.accepted_experience_levels.count() == 2

        assert self.goal_strength in profile.specialisations.all()
        assert self.level_begin in profile.accepted_experience_levels.all()

    def test_matching_logic(self):
        """
        Tests if client can find trainers based on goal and experience
        """

        # Trainer One: Strength and Beginner
        t1 = User.objects.create(
            email=TEST_EMAILS["trainer"], password=TEST_PASSWORD, is_trainer=True
        ).trainer_profile
        t1.specialisations.add(self.goal_strength)
        t1.accepted_experience_levels.add(self.level_begin)

        # Trainer Two: Muscle Mass and Beginner
        t2 = User.objects.create(
            email=TEST_EMAILS["add_trainer"], password=TEST_PASSWORD, is_trainer=True
        ).trainer_profile
        t2.specialisations.add(self.goal_muscle_mass)
        t2.accepted_experience_levels.add(self.level_begin)

        # Client: Strength and Beginner
        c = User.objects.create(
            email=TEST_EMAILS["client"], password=TEST_PASSWORD, is_client=True
        ).client_profile
        c.training_goal = self.goal_strength
        c.experience_level = self.level_begin

        matches = TrainerProfile.objects.filter(
            specialisations=c.training_goal,
            accepted_experience_levels=c.experience_level,
        ).distinct()

        # Assertions
        assert t1 in matches
        assert t2 not in matches

    def test_client_has_choice_of_trainers(self):
        """
        Tests if mutiple trainers can appear in the clients selection pool
        """

        # Trainer One: Strength and Beginner
        t1 = User.objects.create(
            email=TEST_EMAILS["trainer"], password=TEST_PASSWORD, is_trainer=True
        ).trainer_profile
        t1.specialisations.add(self.goal_strength)
        t1.accepted_experience_levels.add(self.level_begin)

        # Trainer Two: Also Strength and Beginner
        t2 = User.objects.create(
            email=TEST_EMAILS["add_trainer"], password=TEST_PASSWORD, is_trainer=True
        ).trainer_profile
        t2.specialisations.add(self.goal_strength)
        t2.accepted_experience_levels.add(self.level_begin)

        # Trainer Three: Muscle Mass and Beginner
        t3 = User.objects.create(
            email=TEST_EMAILS["add_trainer2"], password=TEST_PASSWORD, is_trainer=True
        ).trainer_profile
        t3.specialisations.add(self.goal_muscle_mass)
        t3.accepted_experience_levels.add(self.level_begin)

        # Client: Strength and Beginner
        c = User.objects.create(
            email=TEST_EMAILS["client"], password=TEST_PASSWORD, is_client=True
        ).client_profile
        c.training_goal = self.goal_strength
        c.experience_level = self.level_begin

        matches = TrainerProfile.objects.filter(
            specialisations=c.training_goal,
            accepted_experience_levels=c.experience_level,
        ).distinct()

        # Assertions
        assert t1 in matches
        assert t2 in matches
        assert t3 not in matches
