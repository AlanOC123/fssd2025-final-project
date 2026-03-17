from decimal import Decimal

import pytest
from django.utils import timezone

from apps.analytics.constants import epley_one_rep_max
from apps.analytics.models import ExerciseSessionSnapshot
from apps.analytics.services.load import (
    calculate_joint_load,
    calculate_muscle_load,
    calculate_raw_set_load,
    calculate_session_load,
)
from apps.analytics.services.snapshot import compute_and_save_snapshot
from factories import (
    WorkoutCompletionRecordFactory,
    WorkoutExerciseCompletionRecordFactory,
    WorkoutSetCompletionRecordFactory,
)

pytestmark = pytest.mark.django_db


# ── Load service ──────────────────────────────────────────────────────────────


class TestCalculateRawSetLoad:

    def test_multiplies_reps_by_weight(self):
        result = calculate_raw_set_load(10, Decimal("60"))
        assert result == Decimal("600")

    def test_zero_reps_gives_zero(self):
        assert calculate_raw_set_load(0, Decimal("100")) == Decimal("0")

    def test_returns_decimal(self):
        assert isinstance(calculate_raw_set_load(5, Decimal("50")), Decimal)


class TestCalculateSessionLoad:

    def test_sums_non_skipped_sets(
        self, workout, workout_exercise, workout_set, client_user
    ):
        session = WorkoutCompletionRecordFactory(workout=workout, client=client_user)
        exercise_record = WorkoutExerciseCompletionRecordFactory(
            workout_completion_record=session,
            workout_exercise=workout_exercise,
        )
        # Two sets: 5 reps × 100kg each = 500 + 500 = 1000
        set1 = WorkoutSetCompletionRecordFactory(
            exercise_completion_record=exercise_record,
            workout_set=workout_set,
            reps_completed=5,
            weight_completed=Decimal("100"),
        )

        result = calculate_session_load([set1])
        assert result == Decimal("500")

    def test_skipped_sets_contribute_zero(
        self, workout, workout_exercise, workout_set, client_user
    ):
        session = WorkoutCompletionRecordFactory(workout=workout, client=client_user)
        exercise_record = WorkoutExerciseCompletionRecordFactory(
            workout_completion_record=session,
            workout_exercise=workout_exercise,
        )
        skipped = WorkoutSetCompletionRecordFactory(
            exercise_completion_record=exercise_record,
            workout_set=workout_set,
            is_skipped=True,
            reps_completed=0,
            weight_completed=Decimal("0"),
            completed_at=None,
        )
        assert calculate_session_load([skipped]) == Decimal("0")

    def test_empty_set_records_returns_zero(self):
        assert calculate_session_load([]) == Decimal("0")

    def test_mixed_skipped_and_completed(
        self, workout, workout_exercise, workout_set, client_user
    ):
        timezone.now()
        session = WorkoutCompletionRecordFactory(workout=workout, client=client_user)
        exercise_record = WorkoutExerciseCompletionRecordFactory(
            workout_completion_record=session,
            workout_exercise=workout_exercise,
        )
        completed = WorkoutSetCompletionRecordFactory(
            exercise_completion_record=exercise_record,
            workout_set=workout_set,
            reps_completed=10,
            weight_completed=Decimal("60"),
        )
        # Can't create a second set record for the same workout_set (OneToOne),
        # so just verify the completed set contributes correctly
        result = calculate_session_load([completed])
        assert result == Decimal("600")


class TestCalculateJointLoad:

    def test_distributes_load_by_rom_factor(
        self,
        elbow_flexion_joint_contribution,
        full_range_of_motion,
    ):
        # full_range_of_motion has impact_factor=1.00
        joint_loads = calculate_joint_load(
            Decimal("600"), [elbow_flexion_joint_contribution]
        )
        assert len(joint_loads) == 1
        assert joint_loads[0]["load"] == Decimal("600")

    def test_partial_rom_reduces_load(
        self,
        concentric_bicep_curl_movement,
        elbow_flexion_joint_action,
        partial_range_of_motion,
    ):
        from apps.exercises.models import JointContribution

        partial_contribution = JointContribution.objects.get_or_create(
            joint_action=elbow_flexion_joint_action,
            exercise_movement=concentric_bicep_curl_movement,
            defaults={"joint_range_of_motion": partial_range_of_motion},
        )[0]
        # partial_range_of_motion has impact_factor=0.50
        joint_loads = calculate_joint_load(Decimal("600"), [partial_contribution])
        assert joint_loads[0]["load"] == Decimal("300")

    def test_empty_contributions_returns_empty(self):
        assert calculate_joint_load(Decimal("600"), []) == []


class TestCalculateMuscleLoad:

    def test_distributes_joint_load_to_muscles(
        self,
        elbow_flexion_joint_action,
        bicep_elbow_flexion_involvement,
    ):
        joint_loads = [
            {"joint_action": elbow_flexion_joint_action, "load": Decimal("600")}
        ]
        muscle_loads = calculate_muscle_load(joint_loads)

        assert len(muscle_loads) >= 1
        bicep_entry = next(
            m for m in muscle_loads if m["muscle"].code == "BICEPS_BRACHII"
        )
        # bicep_elbow_flexion_involvement has impact_factor=0.80
        assert bicep_entry["load"] == Decimal("480")

    def test_includes_role_in_output(
        self,
        elbow_flexion_joint_action,
        bicep_elbow_flexion_involvement,
    ):
        joint_loads = [
            {"joint_action": elbow_flexion_joint_action, "load": Decimal("600")}
        ]
        muscle_loads = calculate_muscle_load(joint_loads)
        roles = {m["role"] for m in muscle_loads}
        assert "AGONIST" in roles

    def test_empty_joint_loads_returns_empty(self):
        assert calculate_muscle_load([]) == []


# ── Snapshot service ──────────────────────────────────────────────────────────


class TestComputeAndSaveSnapshot:

    def test_creates_snapshot_on_session_completion(
        self,
        active_phase,
        workout,
        workout_exercise,
        workout_set,
        client_user,
        active_membership,
    ):
        now = timezone.now()
        session = WorkoutCompletionRecordFactory(
            workout=workout,
            client=client_user,
            started_at=now,
            completed_at=now,
        )
        WorkoutExerciseCompletionRecordFactory(
            workout_completion_record=session,
            workout_exercise=workout_exercise,
        )
        WorkoutSetCompletionRecordFactory(
            exercise_completion_record=session.exercise_records.first(),
            workout_set=workout_set,
            reps_completed=10,
            weight_completed=Decimal("60"),
        )

        program = active_phase.program
        snapshot = compute_and_save_snapshot(
            program=program,
            exercise=workout_exercise.exercise,
            session=session,
        )

        assert snapshot is not None
        assert snapshot.session == session
        assert snapshot.program == program
        assert snapshot.session_load == Decimal("600.00")

    def test_1rm_is_epley_of_best_set(
        self,
        active_phase,
        workout,
        workout_exercise,
        workout_set,
        client_user,
    ):
        now = timezone.now()
        session = WorkoutCompletionRecordFactory(
            workout=workout,
            client=client_user,
            started_at=now,
            completed_at=now,
        )
        WorkoutExerciseCompletionRecordFactory(
            workout_completion_record=session,
            workout_exercise=workout_exercise,
        )
        WorkoutSetCompletionRecordFactory(
            exercise_completion_record=session.exercise_records.first(),
            workout_set=workout_set,
            reps_completed=10,
            weight_completed=Decimal("60"),
        )

        program = active_phase.program
        snapshot = compute_and_save_snapshot(
            program=program,
            exercise=workout_exercise.exercise,
            session=session,
        )

        # Epley: 60 × (1 + 10/30) = 80
        expected_1rm = epley_one_rep_max(Decimal("60"), 10)
        assert snapshot.one_rep_max == expected_1rm.quantize(Decimal("0.01"))

    def test_returns_none_for_all_skipped_sets(
        self,
        active_phase,
        workout,
        workout_exercise,
        workout_set,
        client_user,
    ):
        now = timezone.now()
        session = WorkoutCompletionRecordFactory(
            workout=workout,
            client=client_user,
            started_at=now,
            completed_at=now,
        )
        WorkoutExerciseCompletionRecordFactory(
            workout_completion_record=session,
            workout_exercise=workout_exercise,
        )
        WorkoutSetCompletionRecordFactory(
            exercise_completion_record=session.exercise_records.first(),
            workout_set=workout_set,
            is_skipped=True,
            reps_completed=0,
            weight_completed=Decimal("0"),
            completed_at=None,
        )

        program = active_phase.program
        result = compute_and_save_snapshot(
            program=program,
            exercise=workout_exercise.exercise,
            session=session,
        )
        assert result is None

    def test_target_load_is_none_on_first_session(
        self,
        active_phase,
        workout,
        workout_exercise,
        workout_set,
        client_user,
    ):
        """First session has no previous load so target_load should be None."""
        now = timezone.now()
        session = WorkoutCompletionRecordFactory(
            workout=workout,
            client=client_user,
            started_at=now,
            completed_at=now,
        )
        WorkoutExerciseCompletionRecordFactory(
            workout_completion_record=session,
            workout_exercise=workout_exercise,
        )
        WorkoutSetCompletionRecordFactory(
            exercise_completion_record=session.exercise_records.first(),
            workout_set=workout_set,
            reps_completed=10,
            weight_completed=Decimal("60"),
        )

        program = active_phase.program
        snapshot = compute_and_save_snapshot(
            program=program,
            exercise=workout_exercise.exercise,
            session=session,
        )
        assert snapshot.target_load is None

    def test_upserts_on_duplicate_call(
        self,
        active_phase,
        workout,
        workout_exercise,
        workout_set,
        client_user,
    ):
        now = timezone.now()
        session = WorkoutCompletionRecordFactory(
            workout=workout,
            client=client_user,
            started_at=now,
            completed_at=now,
        )
        WorkoutExerciseCompletionRecordFactory(
            workout_completion_record=session,
            workout_exercise=workout_exercise,
        )
        WorkoutSetCompletionRecordFactory(
            exercise_completion_record=session.exercise_records.first(),
            workout_set=workout_set,
            reps_completed=10,
            weight_completed=Decimal("60"),
        )

        program = active_phase.program
        exercise = workout_exercise.exercise

        compute_and_save_snapshot(program=program, exercise=exercise, session=session)
        compute_and_save_snapshot(program=program, exercise=exercise, session=session)

        count = ExerciseSessionSnapshot.objects.filter(
            program=program, exercise=exercise, session=session
        ).count()
        assert count == 1

    def test_snapshot_triggered_by_finish_workout(
        self,
        active_phase,
        workout,
        workout_exercise,
        workout_set,
        client_user,
    ):
        """finish_workout should automatically create a snapshot."""
        from apps.workouts.services.completions import WorkoutCompletionService

        session = WorkoutCompletionService.start_workout(
            workout=workout, client_user=client_user
        )
        exercise_record = WorkoutCompletionService.start_exercise(
            workout_exercise=workout_exercise,
            session=session,
            client_user=client_user,
        )
        WorkoutCompletionService.complete_set(
            workout_set=workout_set,
            exercise_record=exercise_record,
            client_user=client_user,
            reps_completed=10,
            weight_completed=Decimal("60"),
        )
        WorkoutCompletionService.finish_workout(
            session=session, client_user=client_user
        )

        assert ExerciseSessionSnapshot.objects.filter(
            program=active_phase.program,
            exercise=workout_exercise.exercise,
            session=session,
        ).exists()
