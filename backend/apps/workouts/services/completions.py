from django.core.exceptions import ValidationError
from django.db import transaction
from django.utils import timezone

from apps.programs.constants import ProgramPhaseStatusesVocabulary
from apps.workouts.models import (
    Workout,
    WorkoutCompletionRecord,
    WorkoutExercise,
    WorkoutExerciseCompletionRecord,
    WorkoutSet,
    WorkoutSetCompletionRecord,
)


class WorkoutCompletionService:
    """Service layer for managing the lifecycle of workout completion records.

    This service handles starting, finishing, and skipping workouts, exercises,
    and sets, ensuring data integrity and validation against program constraints.
    """

    @staticmethod
    def _now():
        """Returns the current aware datetime."""
        return timezone.now()

    @classmethod
    def _validate_client(cls, client_user):
        """Validates that the user is a valid client capable of recording workouts.

        Args:
            client_user: The User instance to validate.

        Returns:
            The validated client_user instance.

        Raises:
            ValidationError: If the user is missing, malformed, or not a client.
        """
        if not client_user:
            raise ValidationError("Missing clien user.")

        if not hasattr(client_user, "client_profile"):
            raise ValidationError("Malformed client user given.")

        if not client_user.is_client:
            raise ValidationError("Only a client can record a workout completion.")

        return client_user

    @classmethod
    def _validate_phase_is_active(cls, workout):
        """Validates that the workout belongs to an active program phase.

        Args:
            workout: The Workout instance being checked.

        Raises:
            ValidationError: If the program phase is not active.
        """
        phase = workout.program_phase

        if phase.status.code != ProgramPhaseStatusesVocabulary.ACTIVE:
            raise ValidationError(
                "Workouts can only be recorded against an active program phase."
            )

    @classmethod
    def _validate_client_owns_workout(cls, workout, client_user):
        """Validates that the client has a membership for the program being worked out.

        Args:
            workout: The Workout instance.
            client_user: The User instance attempting to record the workout.

        Raises:
            ValidationError: If no active membership exists or if the membership
                belongs to a different user.
        """
        membership = workout.program_phase.program.trainer_client_membership

        if membership is None:
            raise ValidationError(
                "This workout is not attached to an active membership."
            )

        if membership.client.user != client_user:
            raise ValidationError(
                "You can only record workouts for memberships you own."
            )

    @classmethod
    def _validate_no_existing_workout_record(cls, workout):
        """Validates that no completion record already exists for the workout.

        Args:
            workout: The Workout instance.

        Raises:
            ValidationError: If a completion record is already found.
        """
        if WorkoutCompletionRecord.objects.filter(workout=workout).exists():
            raise ValidationError(
                "A completion record already exists for this workout."
            )

    @classmethod
    def _validate_session_is_open(cls, session):
        """Validates that the workout session is currently open for modification.

        Args:
            session: The WorkoutCompletionRecord instance.

        Raises:
            ValidationError: If the session was skipped or is already completed.
        """
        if session.is_skipped:
            raise ValidationError("This workout was skipped and cannot be updated.")
        if session.completed_at is not None:
            raise ValidationError("This workout session is already completed.")

    @classmethod
    def _validate_no_existing_exercise_record(cls, workout_exercise):
        """Validates that no completion record already exists for the exercise.

        Args:
            workout_exercise: The WorkoutExercise instance.

        Raises:
            ValidationError: If an exercise completion record is already found.
        """
        if WorkoutExerciseCompletionRecord.objects.filter(
            workout_exercise=workout_exercise
        ).exists():
            raise ValidationError(
                "A completion record already exists for this exercise."
            )

    @classmethod
    def _validate_exercise_belongs_to_session(cls, workout_exercise, session):
        """Validates that the exercise is part of the provided workout session.

        Args:
            workout_exercise: The WorkoutExercise instance.
            session: The WorkoutCompletionRecord instance.

        Raises:
            ValidationError: If the exercise ID does not match the session's workout ID.
        """
        if workout_exercise.workout_id != session.workout_id:
            raise ValidationError(
                "This exercise does not belong to the workout being recorded."
            )

    @classmethod
    def _validate_exercise_record_is_open(cls, exercise_record):
        """Validates that the exercise completion record is open for modification.

        Args:
            exercise_record: The WorkoutExerciseCompletionRecord instance.

        Raises:
            ValidationError: If the exercise was skipped or is already completed.
        """
        if exercise_record.is_skipped:
            raise ValidationError("This exercise was skipped and cannot be updated.")
        if exercise_record.completed_at is not None:
            raise ValidationError("This exercise is already completed.")

    @classmethod
    def _validate_no_existing_set_record(cls, workout_set):
        """Validates that no completion record already exists for the set.

        Args:
            workout_set: The WorkoutSet instance.

        Raises:
            ValidationError: If a set completion record is already found.
        """
        if WorkoutSetCompletionRecord.objects.filter(workout_set=workout_set).exists():
            raise ValidationError("A completion record already exists for this set.")

    @classmethod
    def _validate_set_belongs_to_exercise(cls, workout_set, exercise_record):
        """Validates that the set is part of the provided exercise completion record.

        Args:
            workout_set: The WorkoutSet instance.
            exercise_record: The WorkoutExerciseCompletionRecord instance.

        Raises:
            ValidationError: If the set's parent exercise ID does not match.
        """
        if workout_set.workout_exercise_id != exercise_record.workout_exercise_id:
            raise ValidationError(
                "This set does not belong to the exercise being recorded."
            )

    # ─── Workout-level actions ────────────────────────────────────────────────

    @classmethod
    @transaction.atomic
    def start_workout(cls, *, workout: Workout, client_user) -> WorkoutCompletionRecord:
        """Starts a new workout session for a client.

        Args:
            workout: The Workout instance to start.
            client_user: The User instance starting the workout.

        Returns:
            The newly created WorkoutCompletionRecord.

        Raises:
            ValidationError: If validation fails.
        """
        cls._validate_client(client_user)
        cls._validate_phase_is_active(workout)
        cls._validate_client_owns_workout(workout, client_user)
        cls._validate_no_existing_workout_record(workout)

        return WorkoutCompletionRecord.objects.create(
            workout=workout,
            client=client_user,
            is_skipped=False,
            started_at=cls._now(),
        )

    @classmethod
    @transaction.atomic
    def skip_workout(cls, *, workout: Workout, client_user) -> WorkoutCompletionRecord:
        """Records a workout as skipped by the client.

        Args:
            workout: The Workout instance to skip.
            client_user: The User instance skipping the workout.

        Returns:
            The newly created WorkoutCompletionRecord marked as skipped.

        Raises:
            ValidationError: If validation fails.
        """
        cls._validate_client(client_user)
        cls._validate_phase_is_active(workout)
        cls._validate_client_owns_workout(workout, client_user)
        cls._validate_no_existing_workout_record(workout)

        now = cls._now()
        return WorkoutCompletionRecord.objects.create(
            workout=workout,
            client=client_user,
            is_skipped=True,
            started_at=now,
            completed_at=now,
        )

    @classmethod
    @transaction.atomic
    def finish_workout(
        cls, *, session: WorkoutCompletionRecord, client_user
    ) -> WorkoutCompletionRecord:
        """Marks an open workout session as completed.

        Args:
            session: The WorkoutCompletionRecord to finish.
            client_user: The User instance finishing the workout.

        Returns:
            The updated WorkoutCompletionRecord with a completion timestamp.

        Raises:
            ValidationError: If the session does not belong to the user or is not open.
        """
        cls._validate_client(client_user)
        cls._validate_session_is_open(session)

        if session.client != client_user:
            raise ValidationError("You can only finish your own workout sessions.")

        session.completed_at = cls._now()
        session.save(update_fields=["completed_at", "updated_at"])

        cls._compute_session_snapshots(session)

        return session

    @classmethod
    def _compute_session_snapshots(cls, session: WorkoutCompletionRecord) -> None:
        """Computes analytics snapshots for exercises performed in the session.

        This captures performance data for non-skipped exercises once the session
        is finalized.

        Args:
            session: The completed WorkoutCompletionRecord.
        """
        from apps.analytics.services.snapshot import compute_and_save_snapshot

        program = session.workout.program_phase.program

        # Group non-skipped exercises to avoid duplicate snapshots for repeats
        exercises = set(
            er.workout_exercise.exercise
            for er in session.exercise_records.filter(
                is_skipped=False,
            ).select_related("workout_exercise__exercise")
        )

        for exercise in exercises:
            compute_and_save_snapshot(
                program=program,
                exercise=exercise,
                session=session,
            )

    # ─── Exercise Actions ─────────────────────────────────────────────────────

    @classmethod
    @transaction.atomic
    def start_exercise(
        cls,
        *,
        workout_exercise: WorkoutExercise,
        session: WorkoutCompletionRecord,
        client_user,
    ) -> WorkoutExerciseCompletionRecord:
        """Starts an exercise within an active workout session.

        Args:
            workout_exercise: The WorkoutExercise being started.
            session: The parent WorkoutCompletionRecord.
            client_user: The User instance starting the exercise.

        Returns:
            The created WorkoutExerciseCompletionRecord.

        Raises:
            ValidationError: If validation fails.
        """
        cls._validate_client(client_user)
        cls._validate_session_is_open(session)
        cls._validate_exercise_belongs_to_session(workout_exercise, session)
        cls._validate_no_existing_exercise_record(workout_exercise)

        return WorkoutExerciseCompletionRecord.objects.create(
            workout_completion_record=session,
            workout_exercise=workout_exercise,
            is_skipped=False,
            started_at=cls._now(),
        )

    @classmethod
    @transaction.atomic
    def skip_exercise(
        cls,
        *,
        workout_exercise: WorkoutExercise,
        session: WorkoutCompletionRecord,
        client_user,
    ) -> WorkoutExerciseCompletionRecord:
        """Marks an exercise as skipped within a workout session.

        Args:
            workout_exercise: The WorkoutExercise being skipped.
            session: The parent WorkoutCompletionRecord.
            client_user: The User instance skipping the exercise.

        Returns:
            The created WorkoutExerciseCompletionRecord marked as skipped.

        Raises:
            ValidationError: If validation fails.
        """
        cls._validate_client(client_user)
        cls._validate_session_is_open(session)
        cls._validate_exercise_belongs_to_session(workout_exercise, session)
        cls._validate_no_existing_exercise_record(workout_exercise)

        now = cls._now()
        return WorkoutExerciseCompletionRecord.objects.create(
            workout_completion_record=session,
            workout_exercise=workout_exercise,
            is_skipped=True,
            started_at=now,
            completed_at=now,
        )

    # ─── Set Actions ──────────────────────────────────────────────────────────

    @classmethod
    @transaction.atomic
    def complete_set(
        cls,
        *,
        workout_set: WorkoutSet,
        exercise_record: WorkoutExerciseCompletionRecord,
        client_user,
        reps_completed: int,
        weight_completed,
        difficulty_rating: int | None = None,
        reps_in_reserve: int | None = None,
    ) -> WorkoutSetCompletionRecord:
        """Records the completion of a specific set with performance data.

        Args:
            workout_set: The WorkoutSet being recorded.
            exercise_record: The parent WorkoutExerciseCompletionRecord.
            client_user: The User instance recording the set.
            reps_completed: Number of repetitions performed.
            weight_completed: The weight load used (Decimal/Float).
            difficulty_rating: Optional RPE/Difficulty score.
            reps_in_reserve: Optional RIR value.

        Returns:
            The created WorkoutSetCompletionRecord.

        Raises:
            ValidationError: If validation fails.
        """
        cls._validate_client(client_user)
        cls._validate_exercise_record_is_open(exercise_record)
        cls._validate_set_belongs_to_exercise(workout_set, exercise_record)
        cls._validate_no_existing_set_record(workout_set)

        return WorkoutSetCompletionRecord.objects.create(
            exercise_completion_record=exercise_record,
            workout_set=workout_set,
            is_skipped=False,
            reps_completed=reps_completed,
            weight_completed=weight_completed,
            difficulty_rating=difficulty_rating,
            reps_in_reserve=reps_in_reserve,
            completed_at=cls._now(),
        )

    @classmethod
    @transaction.atomic
    def skip_set(
        cls,
        *,
        workout_set: WorkoutSet,
        exercise_record: WorkoutExerciseCompletionRecord,
        client_user,
    ) -> WorkoutSetCompletionRecord:
        """Marks a specific set as skipped.

        Args:
            workout_set: The WorkoutSet being skipped.
            exercise_record: The parent WorkoutExerciseCompletionRecord.
            client_user: The User instance skipping the set.

        Returns:
            The created WorkoutSetCompletionRecord marked as skipped.

        Raises:
            ValidationError: If validation fails.
        """
        cls._validate_client(client_user)
        cls._validate_exercise_record_is_open(exercise_record)
        cls._validate_set_belongs_to_exercise(workout_set, exercise_record)
        cls._validate_no_existing_set_record(workout_set)

        return WorkoutSetCompletionRecord.objects.create(
            exercise_completion_record=exercise_record,
            workout_set=workout_set,
            is_skipped=True,
            reps_completed=0,
            weight_completed=0,
            completed_at=cls._now(),
        )
