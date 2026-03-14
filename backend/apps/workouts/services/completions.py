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
    @staticmethod
    def _now():
        return timezone.now()

    @classmethod
    def _validate_client(cls, client_user):
        if not client_user:
            raise ValidationError("Missing client user.")

        if not client_user.is_client:
            raise ValidationError("Only a client can record a workout completion.")

        if not hasattr(client_user, "client_profile"):
            raise ValidationError("Malformed client user given.")

        return client_user

    @classmethod
    def _validate_phase_is_active(cls, workout):
        phase = workout.program_phase

        if phase.status.code != ProgramPhaseStatusesVocabulary.ACTIVE:
            raise ValidationError(
                "Workouts can only be recorded against an active program phase."
            )

    @classmethod
    def _validate_client_owns_workout(cls, workout, client_user):
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
        if WorkoutCompletionRecord.objects.filter(workout=workout).exists():
            raise ValidationError(
                "A completion record already exists for this workout."
            )

    @classmethod
    def _validate_session_is_open(cls, session):
        if session.is_skipped:
            raise ValidationError("This workout was skipped and cannot be updated.")
        if session.completed_at is not None:
            raise ValidationError("This workout session is already completed.")

    @classmethod
    def _validate_no_existing_exercise_record(cls, workout_exercise):
        if WorkoutExerciseCompletionRecord.objects.filter(
            workout_exercise=workout_exercise
        ).exists():
            raise ValidationError(
                "A completion record already exists for this exercise."
            )

    @classmethod
    def _validate_exercise_belongs_to_session(cls, workout_exercise, session):
        if workout_exercise.workout_id != session.workout_id:
            raise ValidationError(
                "This exercise does not belong to the workout being recorded."
            )

    @classmethod
    def _validate_exercise_record_is_open(cls, exercise_record):
        if exercise_record.is_skipped:
            raise ValidationError("This exercise was skipped and cannot be updated.")
        if exercise_record.completed_at is not None:
            raise ValidationError("This exercise is already completed.")

    @classmethod
    def _validate_no_existing_set_record(cls, workout_set):
        if WorkoutSetCompletionRecord.objects.filter(workout_set=workout_set).exists():
            raise ValidationError("A completion record already exists for this set.")

    @classmethod
    def _validate_set_belongs_to_exercise(cls, workout_set, exercise_record):
        if workout_set.workout_exercise_id != exercise_record.workout_exercise_id:
            raise ValidationError(
                "This set does not belong to the exercise being recorded."
            )

    # ─── Workout-level actions ────────────────────────────────────────────────

    @classmethod
    @transaction.atomic
    def start_workout(cls, *, workout: Workout, client_user) -> WorkoutCompletionRecord:
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
        cls._validate_client(client_user)
        cls._validate_session_is_open(session)

        if session.client != client_user:
            raise ValidationError("You can only finish your own workout sessions.")

        session.completed_at = cls._now()
        session.save(update_fields=["completed_at", "updated_at"])
        return session

    #  Exercise Actions

    @classmethod
    @transaction.atomic
    def start_exercise(
        cls,
        *,
        workout_exercise: WorkoutExercise,
        session: WorkoutCompletionRecord,
        client_user,
    ) -> WorkoutExerciseCompletionRecord:
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

    # Set Actions

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
