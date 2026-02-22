import pytest
from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from django.db import IntegrityError

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

    @pytest.fixture(autouse=True)
    def setup_data(self):
        """
        Run before tests to ensure the dependant data exists.
        """
        # Create the look ups
        self.goal = TrainingGoal.objects.create(goal_name="Strength")
        self.level = ExperienceLevel.objects.create(level_name="Advanced")
        self.status = MembershipStatus.objects.create(status_name="ACTIVE")

        # Create the actions
        t_user = User.objects.create(email="coach@apex.com", is_trainer=True)
        c_user = User.objects.create(email="client@apex.com", is_client=True)

        # Create the membership bridge
        self.membership = TrainerClientMembership.objects.create(
            trainer=t_user.trainer_profile,
            client=c_user.client_profile,
            status=self.status,
        )

        # Create the phases
        self.phase_opt_1 = ProgramPhaseOption.objects.create(
            phase_name="Accumulation",
            order_index=1,
            default_duration=4,
            description="High Volume",
        )

        self.phase_opt_2 = ProgramPhaseOption.objects.create(
            phase_name="Intensity",
            order_index=2,
            default_duration=3,
            description="High Load",
        )

    def test_program_creation(self):
        """Test basic program creation linked to membership"""

        # Create the program
        program = Program.objects.create(
            program_name="Winter Arc",
            trainer_client_membership=self.membership,
            trainer_goal=self.goal,
            experience_level=self.level,
        )

        # Assertions
        assert program.program_name == "Winter Arc"
        assert program.trainer_client_membership == self.membership

    def test_duration_calculation(self):
        """Test calculated field of the program derived from phases"""

        program = Program.objects.create(
            program_name="Winter Arc",
            trainer_client_membership=self.membership,
            trainer_goal=self.goal,
            experience_level=self.level,
        )

        # Append phases to the program
        ProgramPhase.objects.create(program=program, phase_option=self.phase_opt_1)
        ProgramPhase.objects.create(program=program, phase_option=self.phase_opt_2)

        # Assert derived duration
        assert program.calculated_duration == 7

    def test_duration_calculation_override(self):
        """Test the calculated field gets overriden when provided a value"""

        program = Program.objects.create(
            program_name="Winter Arc",
            trainer_client_membership=self.membership,
            trainer_goal=self.goal,
            experience_level=self.level,
        )

        # Add a custom duration
        custom_phase = ProgramPhase.objects.create(
            program=program, phase_option=self.phase_opt_1, custom_duration=6
        )

        ProgramPhase.objects.create(program=program, phase_option=self.phase_opt_2)

        assert custom_phase.custom_duration == 6
        assert program.calculated_duration == 9

    def test_duration_zero_phase(self):
        """Tests fallback value for calculated duration logic"""
        program = Program.objects.create(
            program_name="Winter Arc",
            trainer_client_membership=self.membership,
            trainer_goal=self.goal,
            experience_level=self.level,
        )

        # No phases, should equal 0
        assert program.calculated_duration == 0

    def test_phase_ordering_and_active_state(self):
        """Tests structural and flags on phases"""

        program = Program.objects.create(
            program_name="Winter Arc",
            trainer_client_membership=self.membership,
            trainer_goal=self.goal,
            experience_level=self.level,
        )

        p1 = ProgramPhase.objects.create(
            program=program, phase_option=self.phase_opt_1, is_completed=True
        )
        p2 = ProgramPhase.objects.create(
            program=program, phase_option=self.phase_opt_2, is_active=True
        )

        # Assert Flags
        assert p1.is_completed
        assert p2.is_active

        # Assert ordering
        assert p1.phase_option.order_index < p2.phase_option.order_index

    def test_safeguard_mutually_exclusive(self):
        program = Program.objects.create(
            program_name="Winter Arc",
            trainer_client_membership=self.membership,
            trainer_goal=self.goal,
            experience_level=self.level,
        )

        # Mutually exclusive state conflict
        p1 = ProgramPhase(
            program=program,
            phase_option=self.phase_opt_1,
            is_completed=True,
            is_active=True,
        )

        # Assert this raises
        with pytest.raises(ValidationError):
            p1.save()

    def test_safeguard_single_active(self):
        program = Program.objects.create(
            program_name="Winter Arc",
            trainer_client_membership=self.membership,
            trainer_goal=self.goal,
            experience_level=self.level,
        )

        # Set P1 to be active phase
        p1 = ProgramPhase.objects.create(
            program=program,
            phase_option=self.phase_opt_1,
            is_active=True,
        )

        # Set P2 to be active phase
        p2 = ProgramPhase.objects.create(
            program=program,
            phase_option=self.phase_opt_2,
            is_active=True,
        )

        # Refresh P1
        p1.refresh_from_db()

        # Assert P1 is now inactive
        assert p1.is_active is not True
        assert p2.is_active is True

    def test_safeguard_phase_uniqueness(self):
        program = Program.objects.create(
            program_name="Winter Arc",
            trainer_client_membership=self.membership,
            trainer_goal=self.goal,
            experience_level=self.level,
        )

        # Set P1 to be phase opt 1
        ProgramPhase.objects.create(
            program=program,
            phase_option=self.phase_opt_1,
        )

        # Try create phase opt 1 again. Should fail
        with pytest.raises(IntegrityError):
            ProgramPhase.objects.create(
                program=program,
                phase_option=self.phase_opt_1,
            )
