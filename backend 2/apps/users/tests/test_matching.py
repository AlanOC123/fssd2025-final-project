import pytest
from django.contrib.auth import get_user_model
from model_bakery import baker

from apps.users.models import (
    ClientProfile,
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

    @pytest.fixture(autouse=True)
    def setup_method(self):
        # Create look up data
        self.goal_strength = baker.make(TrainingGoal, goal_name="Strength")
        self.goal_muscle_mass = baker.make(TrainingGoal, goal_name="Muscle Mass")

        self.level_begin = baker.make(ExperienceLevel, level_name="Beginner")
        self.level_inter = baker.make(ExperienceLevel, level_name="Intermediate")

        self.client = baker.make(ClientProfile)
        self.trainer_a = baker.make(TrainerProfile)
        self.trainer_b = baker.make(TrainerProfile)
        self.trainer_c = baker.make(TrainerProfile)

    def test_client_constraints_single_selection(self):
        """
        Tests if a user can only add exactly 1 goal and 1 level
        """

        # Set initial values
        self.client.training_goal = self.goal_strength
        self.client.experience_level = self.level_begin
        self.client.save()

        # Verify
        assert self.client.training_goal == self.goal_strength
        assert self.client.experience_level == self.level_begin

        # Try update
        self.client.training_goal = self.goal_muscle_mass
        self.client.save()

        # Verify it updated not added on top
        assert self.client.training_goal == self.goal_muscle_mass
        assert self.client.training_goal != self.goal_strength

    def test_trainer_constraints_many_selections(self):
        user = User.objects.create(
            email=TEST_EMAILS["trainer"], password=TEST_PASSWORD, is_trainer=True
        )

        self.trainer_a.specialisations.add(self.goal_strength, self.goal_muscle_mass)

        self.trainer_a.accepted_experience_levels.add(
            self.level_begin, self.level_inter
        )

        self.trainer_a.save()

        assert self.trainer_a.specialisations.count() == 2
        assert self.trainer_a.accepted_experience_levels.count() == 2

        assert self.goal_strength in self.trainer_a.specialisations.all()
        assert self.level_begin in self.trainer_a.accepted_experience_levels.all()

    def test_matching_logic(self):
        """
        Tests if client can find trainers based on goal and experience
        """

        # Trainer One: Strength and Beginner
        self.trainer_a.specialisations.add(self.goal_strength)
        self.trainer_a.accepted_experience_levels.add(self.level_begin)

        # Trainer Two: Muscle Mass and Beginner
        self.trainer_b.specialisations.add(self.goal_muscle_mass)
        self.trainer_b.accepted_experience_levels.add(self.level_begin)

        # Client: Strength and Beginner
        self.client.training_goal = self.goal_strength
        self.client.experience_level = self.level_begin

        matches = TrainerProfile.objects.filter(
            specialisations=self.client.training_goal,
            accepted_experience_levels=self.client.experience_level,
        ).distinct()

        # Assertions
        assert self.trainer_a in matches
        assert self.trainer_b not in matches

    def test_client_has_choice_of_trainers(self):
        """
        Tests if mutiple trainers can appear in the clients selection pool
        """

        # Trainer One: Strength and Beginner
        self.trainer_a.specialisations.add(self.goal_strength)
        self.trainer_a.accepted_experience_levels.add(self.level_begin)

        # Trainer Two: Also Strength and Beginner
        self.trainer_b.specialisations.add(self.goal_strength)
        self.trainer_b.accepted_experience_levels.add(self.level_begin)

        # Trainer Three: Muscle Mass and Beginner
        self.trainer_c.specialisations.add(self.goal_muscle_mass)
        self.trainer_c.accepted_experience_levels.add(self.level_begin)

        # Client: Strength and Beginner
        self.client.training_goal = self.goal_strength
        self.client.experience_level = self.level_begin

        matches = TrainerProfile.objects.filter(
            specialisations=self.client.training_goal,
            accepted_experience_levels=self.client.experience_level,
        ).distinct()

        # Assertions
        assert self.trainer_a in matches
        assert self.trainer_b in matches
        assert self.trainer_c not in matches
