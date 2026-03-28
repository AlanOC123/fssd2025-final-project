"""Management command to backfill exercise session snapshots.

This command computes and saves ExerciseSessionSnapshot rows for every completed
WorkoutCompletionRecord that does not already have associated snapshots. This is
typically used after seeding demo data or when the snapshot service is
introduced to a system with historical data.
"""

from django.core.management.base import BaseCommand
from django.db import transaction

from apps.analytics.services.snapshot import compute_and_save_snapshot
from apps.workouts.models import WorkoutCompletionRecord


class Command(BaseCommand):
    """Command to compute missing snapshots for completed workout sessions.

    Iterates through completed, non-skipped sessions and triggers the snapshot
    service for each associated exercise.
    """

    help = "Backfill ExerciseSessionSnapshot for all completed sessions missing them."

    def add_arguments(self, parser):
        """Defines the command line arguments for the backfill command.

        Args:
            parser: The argument parser instance.
        """
        parser.add_argument(
            "--dry-run",
            action="store_true",
            help="Report what would be computed without writing to the DB.",
        )

    def handle(self, *args, **options):
        """Executes the backfill logic.

        Finds eligible sessions, iterates through their exercises, and invokes
         the snapshot computation service within atomic transactions.

        Args:
            *args: Variable length argument list.
            **options: A dictionary of command line arguments (e.g., dry_run).
        """
        dry_run = options["dry_run"]

        # Find completed, non-skipped sessions that have exercise records
        # and are currently missing snapshots.
        sessions = (
            WorkoutCompletionRecord.objects.filter(
                completed_at__isnull=False,
                is_skipped=False,
            )
            .exclude(
                # Skip sessions that already have all their snapshots
                exercise_snapshots__isnull=False,
            )
            .select_related(
                "workout__program_phase__program__experience_level",
                "workout__program_phase__program__training_goal",
            )
            .prefetch_related(
                "exercise_records__workout_exercise__exercise",
                "exercise_records__set_records",
            )
            .distinct()
        )

        total = sessions.count()
        self.stdout.write(f"Found {total} session(s) missing snapshots.")

        if dry_run:
            self.stdout.write(self.style.WARNING("--- DRY RUN MODE ---"))
            for session in sessions:
                program = session.workout.program_phase.program
                exercises = {
                    er.workout_exercise.exercise
                    for er in session.exercise_records.filter(is_skipped=False)
                }
                self.stdout.write(
                    f"  Would compute: session={session.id} "
                    f"program={program.program_name} "
                    f"exercises={[e.exercise_name for e in exercises]}"
                )
            return

        created = 0
        skipped = 0
        errors = 0

        for session in sessions:
            program = session.workout.program_phase.program
            # Prefetch exercise records to avoid N+1 queries during the inner loop
            exercises = {
                er.workout_exercise.exercise
                for er in session.exercise_records.filter(
                    is_skipped=False
                ).select_related("workout_exercise__exercise")
            }

            for exercise in exercises:
                try:
                    with transaction.atomic():
                        snapshot = compute_and_save_snapshot(
                            program=program,
                            exercise=exercise,
                            session=session,
                        )
                        if snapshot:
                            created += 1
                        else:
                            # If the service returns None, it usually means
                            # there was no relevant load to capture.
                            skipped += 1
                except Exception as e:
                    errors += 1
                    self.stderr.write(
                        f"  Error on session={session.id} "
                        f"exercise={exercise.exercise_name}: {e}"
                    )

        self.stdout.write(
            self.style.SUCCESS(
                f"Done. Created: {created}, Skipped (no load): {skipped}, Errors: {errors}"
            )
        )
