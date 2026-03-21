"""
Management command: backfill_snapshots

Computes and saves ExerciseSessionSnapshot rows for every completed
WorkoutCompletionRecord that doesn't already have snapshots.

Run once after seeding demo data, or any time completion records exist
without corresponding snapshots (e.g. if the snapshot service was added
after historical data was already in the DB).

Usage:
    python manage.py backfill_snapshots
    python manage.py backfill_snapshots --dry-run
"""

from django.core.management.base import BaseCommand
from django.db import transaction

from apps.analytics.services.snapshot import compute_and_save_snapshot
from apps.workouts.models import WorkoutCompletionRecord


class Command(BaseCommand):
    help = "Backfill ExerciseSessionSnapshot for all completed sessions missing them."

    def add_arguments(self, parser):
        parser.add_argument(
            "--dry-run",
            action="store_true",
            help="Report what would be computed without writing to the DB.",
        )

    def handle(self, *args, **options):
        dry_run = options["dry_run"]

        # Find completed, non-skipped sessions that have exercise records
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
                            skipped += 1
                except Exception as e:
                    errors += 1
                    self.stderr.write(
                        f"  Error on session={session.id} exercise={exercise.exercise_name}: {e}"
                    )

        self.stdout.write(
            self.style.SUCCESS(
                f"Done. Created: {created}, Skipped (no load): {skipped}, Errors: {errors}"
            )
        )
