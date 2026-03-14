import pytest
from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from django.db import IntegrityError
from model_bakery import baker

from apps.programs.models import Program, ProgramPhase, ProgramPhaseOption
from apps.users.models import (
    ExperienceLevel,
    MembershipStatus,
    TrainerClientMembership,
    TrainingGoal,
)

User = get_user_model()


@pytest.mark.django_db
class TestProgramLogic:
    """Test the interaction and creation of a Program specifically"""

    @pytest.fixture(autouse=True)
    def setup_data(self):
        """
        Run before tests to ensure the dependant data exists.
        """
        # Create the look ups
        self.goal = baker.make(TrainingGoal, goal_name="Strength")
        self.level = baker.make(ExperienceLevel, level_name="Beginner")
        self.status_active = baker.make(MembershipStatus, status_name="ACTIVE")
        self.status_pending = baker.make(
            MembershipStatus, status_name="PENDING TRAINER REVIEW"
        )

        # Create a few trainers
        self.t1 = baker.make(User, is_trainer=True)
        self.t2 = baker.make(User, is_trainer=True)
        self.t3 = baker.make(User, is_trainer=True)

        # Create a few clients
        self.c1 = baker.make(User, is_client=True)
        self.c2 = baker.make(User, is_client=True)
        self.c3 = baker.make(User, is_client=True)

        # Create a few memberships
        self.mem_a = baker.make(
            TrainerClientMembership,
            trainer=self.t1.trainer_profile,
            client=self.c1.client_profile,
            status=self.status_active,
        )

        self.mem_b = baker.make(
            TrainerClientMembership,
            trainer=self.t2.trainer_profile,
            client=self.c2.client_profile,
            status=self.status_active,
        )

        self.mem_inactive = baker.make(
            TrainerClientMembership,
            trainer=self.t3.trainer_profile,
            client=self.c3.client_profile,
            status=self.status_pending,
        )

    def test_program_creation(self):
        """Test basic program creation linked to membership"""

        # Create the program
        program = baker.make(
            Program,
            program_name="Winter Arc",
            training_goal=self.goal,
            experience_level=self.level,
            trainer_client_membership=self.mem_a,
        )

        # Assertions
        assert program.program_name == "Winter Arc"
        assert program.trainer_client_membership == self.mem_a

    def test_program_only_created_on_active_membership(self):
        """Tests a program cannot be created on an inactive membership"""

        # Prepare a program
        program = baker.prepare(
            Program,
            program_name="Winter Arc",
            training_goal=self.goal,
            experience_level=self.level,
            trainer_client_membership=self.mem_inactive,
        )

        # Try save
        with pytest.raises(ValidationError):
            program.save()


@pytest.mark.django_db
class TestProgramPhaseLogic:
    """Tests the features for the granular logic of the programs"""

    @pytest.fixture(autouse=True)
    def setup_data(self):
        # Create the look ups
        self.goal = baker.make(TrainingGoal, goal_name="Strength")
        self.level = baker.make(ExperienceLevel, level_name="Beginner")
        self.status_active = baker.make(MembershipStatus, status_name="ACTIVE")
        self.status_pending = baker.make(
            MembershipStatus, status_name="PENDING TRAINER REVIEW"
        )

        # Create phase options
        self.p_opt1 = baker.make(
            ProgramPhaseOption,
            phase_name="Foundation",
            order_index=1,
            default_duration=4,
            description="Introductory phase focused on technique, joint health,"
            "and preparing the body for training stress.",
        )

        self.p_opt2 = baker.make(
            ProgramPhaseOption,
            phase_name="Accumulation",
            order_index=2,
            default_duration=6,
            description="Focus on increasing total work capacity. "
            "Ideal for muscle growth (Hypertrophy) or endurance goals.",
        )

        # Create a few trainers
        self.t1 = baker.make(User, is_trainer=True)
        self.t2 = baker.make(User, is_trainer=True)
        self.t3 = baker.make(User, is_trainer=True)

        # Create a few clients
        self.c1 = baker.make(User, is_client=True)
        self.c2 = baker.make(User, is_client=True)
        self.c3 = baker.make(User, is_client=True)

        # Create a few memberships
        self.mem_a = baker.make(
            TrainerClientMembership,
            trainer=self.t1.trainer_profile,
            client=self.c1.client_profile,
            status=self.status_active,
        )

        self.mem_b = baker.make(
            TrainerClientMembership,
            trainer=self.t2.trainer_profile,
            client=self.c2.client_profile,
            status=self.status_active,
        )

        # Create some programs
        self.program_1 = baker.make(
            Program,
            program_name="Winter Arc",
            training_goal=self.goal,
            experience_level=self.level,
            trainer_client_membership=self.mem_a,
        )

        self.program_2 = baker.make(
            Program,
            program_name="Summer Shred",
            training_goal=self.goal,
            experience_level=self.level,
            trainer_client_membership=self.mem_b,
        )

    def test_program_phase_connection(self):
        """Tests creation of a program phase"""

        prog_phase = baker.make(
            ProgramPhase,
            phase_option=self.p_opt1,
            program=self.program_1,
            is_active=True,
            is_completed=False,
            custom_duration=6,
        )

        assert prog_phase.program == self.program_1
        assert prog_phase.is_active is True
        assert prog_phase.is_completed is False
        assert prog_phase.custom_duration == 6
