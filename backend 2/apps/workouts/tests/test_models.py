import pytest
from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from django.db import IntegrityError
from django.utils import timezone

from apps.exercises.models import Exercise
from apps.programs.models import Program, ProgramPhase, ProgramPhaseOption
from apps.users.models import (
    ExperienceLevel,
    MembershipStatus,
    TrainerClientMembership,
    TrainingGoal,
)
from apps.workouts.models import (
    Workout,
    WorkoutCompletionRecord,
    WorkoutExercise,
    WorkoutExerciseCompletionRecord,
    WorkoutSet,
    WorkoutSetCompletionRecord,
)

User = get_user_model()


@pytest.mark.django_db
class TestWorkoutLogic:

    @pytest.fixture(autouse=True)
    def setup_data(self):
        # Setup Base Data (Users, Membership, Program)
        trainer = User.objects.create(
            email="coach@test.com", is_trainer=True
        ).trainer_profile
        client = User.objects.create(
            email="athlete@test.com", is_client=True
        ).client_profile
        status = MembershipStatus.objects.create(status_name="ACTIVE")
        membership = TrainerClientMembership.objects.create(
            trainer=trainer, client=client, status=status
        )

        goal = TrainingGoal.objects.create(goal_name="Strength")
        level = ExperienceLevel.objects.create(level_name="Advanced")

        program = Program.objects.create(
            program_name="Test Program",
            trainer_client_membership=membership,
            training_goal=goal,
            experience_level=level,
        )

        phase_opt = ProgramPhaseOption.objects.create(
            phase_name="Test Phase", order_index=1
        )
        self.phase = ProgramPhase.objects.create(
            program=program, phase_option=phase_opt
        )

        # Setup Exercise
        self.exercise = Exercise.objects.create(
            exercise_name="Test Squat", api_name="Squat", experience_level=level
        )

    def test_workout_structure_creation(self):
        """Test creating the Prescription hierarchy"""

        # Create the workout container
        workout = Workout.objects.create(
            workout_name="Leg Day",
            estimated_duration_s=(60 * 60),
            program_phase=self.phase,
        )

        # Create the associated exercise
        w_exercise = WorkoutExercise.objects.create(
            workout=workout, exercise=self.exercise, order=1, sets_prescribed=3
        )

        # Create a workout set
        w_set = WorkoutSet.objects.create(
            workout_exercise=w_exercise,
            set_order=1,
            reps_prescribed=5,
            weight_prescribed=100.00,
        )

        # Assertions
        assert workout.workout_name == "Leg Day"
        assert workout.estimated_duration_s == 60 * 60
        assert workout.exercises.count() == 1
        assert w_exercise.sets.count() == 1
        assert w_set.weight_prescribed == 100.00

    def test_full_adherence_log_hierarchy(self):
        # Prescription
        workout = Workout.objects.create(
            workout_name="Leg Day",
            estimated_duration_s=(60 * 60),
            program_phase=self.phase,
        )

        w_ex = WorkoutExercise.objects.create(
            workout=workout, exercise=self.exercise, order=1, sets_prescribed=1
        )

        w_s = WorkoutSet.objects.create(
            workout_exercise=w_ex,
            set_order=1,
            reps_prescribed=5,
            weight_prescribed=100.00,
        )

        # Completion Records

        w_log = WorkoutCompletionRecord.objects.create(
            workout=workout,
            completed_at=timezone.now(),
            is_skipped=False,
            time_taken_s=3600,
        )

        ex_log = WorkoutExerciseCompletionRecord.objects.create(
            workout_completion_record=w_log,
            workout_exercise=w_ex,
            completed_at=timezone.now(),
            is_skipped=False,
            difficulty_rating=8,
        )

        set_log = WorkoutSetCompletionRecord.objects.create(
            exercise_completion_record=ex_log,
            workout_set=w_s,
            reps_completed=5,
            weight_completed=100.00,
            completed_at=timezone.now(),
            reps_in_reserve=2,
            is_skipped=False,
        )

        # Traversal

        found_sets = WorkoutSetCompletionRecord.objects.filter(
            exercise_completion_record__workout_completion_record=w_log
        )

        assert found_sets.count() == 1
        assert found_sets.first() == set_log

    def test_partial_adherence_log(self):
        """
        Tests differences between a partially completed
        and connected prescribed record
        """

        workout = Workout.objects.create(
            workout_name="Leg Day",
            estimated_duration_s=(60 * 60),
            program_phase=self.phase,
        )

        w_ex = WorkoutExercise.objects.create(
            workout=workout, exercise=self.exercise, order=1, sets_prescribed=1
        )

        w_s = WorkoutSet.objects.create(
            workout_exercise=w_ex,
            set_order=1,
            reps_prescribed=5,
            weight_prescribed=100.00,
        )

        # Completed in less time
        w_log = WorkoutCompletionRecord.objects.create(
            workout=workout,
            completed_at=timezone.now(),
            is_skipped=False,
            time_taken_s=3200,
        )

        ex_log = WorkoutExerciseCompletionRecord.objects.create(
            workout_completion_record=w_log,
            workout_exercise=w_ex,
            completed_at=timezone.now(),
            is_skipped=False,
            difficulty_rating=8,
        )

        # Completed with less reps
        set_log = WorkoutSetCompletionRecord.objects.create(
            exercise_completion_record=ex_log,
            workout_set=w_s,
            reps_completed=3,
            weight_completed=100.00,
            completed_at=timezone.now(),
            reps_in_reserve=2,
            is_skipped=False,
        )

        #
        assert w_log.time_taken_s < workout.estimated_duration_s
        assert w_s.reps_prescribed > set_log.reps_completed

    def test_skipped_workout(self):
        workout = Workout.objects.create(
            workout_name="Leg Day",
            estimated_duration_s=(60 * 60),
            program_phase=self.phase,
        )

        w_log = WorkoutCompletionRecord.objects.create(
            workout=workout, time_taken_s=0, is_skipped=True
        )

        # Should have no associated exercises and be skipped
        assert w_log.exercise_records.count() == 0
        assert workout.completion_record.is_skipped

    def test_one_to_one_constraint(self):
        """Tests a workout can only have 1 completion record"""
        workout = Workout.objects.create(
            workout_name="Leg Day",
            estimated_duration_s=(60 * 60),
            program_phase=self.phase,
        )

        # First log
        WorkoutCompletionRecord.objects.create(
            workout=workout, time_taken_s=3600, completed_at=timezone.now()
        )

        # Duplicate Log (Should fail)
        with pytest.raises(IntegrityError):
            WorkoutCompletionRecord.objects.create(
                workout=workout, time_taken_s=3600, completed_at=timezone.now()
            )

    def test_safeguard_skipped_cannot_have_duration(self):
        """Test that you cannot say 'I skipped this' but also 'It took me 1 hour'"""
        workout = Workout.objects.create(
            workout_name="Confused Logic",
            estimated_duration_s=3600,
            program_phase=self.phase,
        )

        with pytest.raises(ValidationError):
            WorkoutCompletionRecord.objects.create(
                workout=workout,
                time_taken_s=3600,
                is_skipped=True,
                completed_at=timezone.now(),
            )

        def test_safeguard_skipped_cannot_have_children(self):
            """Test that you cannot add exercises to a skipped workout"""
            workout = Workout.objects.create(
                workout_name="Ghost Logic",
                estimated_duration_s=3600,
                program_phase=self.phase,
            )
            w_exercise = WorkoutExercise.objects.create(
                workout=workout, exercise=self.exercise, order=1, sets_prescribed=1
            )

            # Create the Skipped Parent
            w_log = WorkoutCompletionRecord.objects.create(
                workout=workout,
                time_taken_s=0,
                is_skipped=True,
                completed_at=timezone.now(),
            )

            # Try to attach a child record (Should fail)
            with pytest.raises(ValidationError):
                WorkoutExerciseCompletionRecord.objects.create(
                    workout_completion_record=w_log,
                    workout_exercise=w_exercise,
                    difficulty_rating=5,
                )
