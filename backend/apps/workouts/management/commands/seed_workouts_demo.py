import json
import os
from datetime import timedelta
from decimal import Decimal

from django.contrib.auth import get_user_model
from django.core.management.base import BaseCommand
from django.utils import timezone

from apps.exercises.models import Exercise
from apps.programs.constants import ProgramPhaseStatusesVocabulary
from apps.programs.models import Program
from apps.workouts.models import (
    Workout,
    WorkoutCompletionRecord,
    WorkoutExercise,
    WorkoutExerciseCompletionRecord,
    WorkoutSet,
    WorkoutSetCompletionRecord,
)

User = get_user_model()


class Command(BaseCommand):
    help = "Seeds workout history and future sessions for the demo program"

    def handle(self, *args, **kwargs):
        base_dir = os.path.dirname(__file__)
        file_path = os.path.join(base_dir, "seed_workouts_demo_data.json")

        try:
            with open(file_path) as f:
                data = json.load(f)
                self.stdout.write("Seeding Workout Demo Data...")

            # ── Resolve program and client ─────────────────────────────────────

            try:
                client_user = User.objects.get(email=data["client_email"])
                program = Program.objects.get(
                    program_name=data["program_name"],
                    trainer_client_membership__client__user=client_user,
                )
            except Exception as e:
                self.stdout.write(self.style.ERROR(f"Setup error: {e}"))
                return

            today = timezone.localdate()
            timezone.now()

            # ── Process each phase ────────────────────────────────────────────

            for phase in program.phases.order_by("sequence_order"):
                phase_code = phase.phase_option.code
                status = phase.status.code

                if phase_code not in data["routines"]:
                    self.stdout.write(f"    Skipping phase '{phase_code}' (no routine)")
                    continue

                if status == ProgramPhaseStatusesVocabulary.PLANNED:
                    self.stdout.write(f"    Skipping planned phase '{phase_code}'")
                    continue

                routine = data["routines"][phase_code]
                schedule = routine["schedule"]
                workouts = routine["workouts"]
                workout_idx = 0

                # Derive date window for this phase
                if status == ProgramPhaseStatusesVocabulary.COMPLETED:
                    start_date = phase.actual_start_date
                    end_date = phase.actual_end_date
                elif status == ProgramPhaseStatusesVocabulary.ACTIVE:
                    start_date = phase.actual_start_date or (today - timedelta(days=7))
                    end_date = today  # only generate up to today for active phases
                else:
                    continue

                self.stdout.write(
                    f"    Processing: {phase_code} ({start_date} → {end_date})"
                )

                current_date = start_date
                while current_date <= end_date:
                    if current_date.weekday() in schedule:
                        template = workouts[workout_idx % len(workouts)]
                        workout_idx += 1
                        weeks_in = (current_date - start_date).days // 7

                        # Progressive overload: +1.25kg per week
                        overload = weeks_in * Decimal("1.25")

                        workout = Workout.objects.create(
                            workout_name=f"{template['name']} — Week {weeks_in + 1}",
                            program_phase=phase,
                            planned_date=current_date,
                        )

                        is_past = current_date < today
                        session = None
                        session_dt = timezone.datetime.combine(
                            current_date,
                            timezone.datetime.min.time(),
                            tzinfo=timezone.get_current_timezone(),
                        )

                        if is_past:
                            session = WorkoutCompletionRecord.objects.create(
                                workout=workout,
                                client=client_user,
                                is_skipped=False,
                                started_at=session_dt,
                                completed_at=session_dt + timedelta(hours=1),
                            )

                        for idx, ex_data in enumerate(template["exercises"]):
                            try:
                                exercise = Exercise.objects.get(
                                    exercise_name=ex_data["name"]
                                )
                            except Exercise.DoesNotExist:
                                self.stdout.write(
                                    self.style.WARNING(
                                        f"        Exercise '{ex_data['name']}' not found — run seed_exercises first"
                                    )
                                )
                                continue

                            target_weight = (
                                Decimal(str(ex_data["start_weight"])) + overload
                            )

                            w_exercise = WorkoutExercise.objects.create(
                                workout=workout,
                                exercise=exercise,
                                order=idx + 1,
                                sets_prescribed=ex_data["sets"],
                            )

                            ex_record = None
                            if is_past and session:
                                ex_record = (
                                    WorkoutExerciseCompletionRecord.objects.create(
                                        workout_completion_record=session,
                                        workout_exercise=w_exercise,
                                        is_skipped=False,
                                        started_at=session_dt,
                                        completed_at=session_dt
                                        + timedelta(minutes=15 * (idx + 1)),
                                    )
                                )

                            for set_num in range(1, ex_data["sets"] + 1):
                                w_set = WorkoutSet.objects.create(
                                    workout_exercise=w_exercise,
                                    set_order=set_num,
                                    reps_prescribed=ex_data["reps"],
                                    weight_prescribed=target_weight,
                                )

                                if is_past and ex_record:
                                    WorkoutSetCompletionRecord.objects.create(
                                        exercise_completion_record=ex_record,
                                        workout_set=w_set,
                                        is_skipped=False,
                                        reps_completed=ex_data["reps"],
                                        weight_completed=target_weight,
                                        difficulty_rating=ex_data["rpe"],
                                        reps_in_reserve=2,
                                        completed_at=session_dt
                                        + timedelta(
                                            minutes=15 * (idx + 1) + set_num * 3
                                        ),
                                    )

                    current_date += timedelta(days=1)

                self.stdout.write(
                    self.style.SUCCESS(f"    Completed phase: {phase_code}")
                )

        except FileNotFoundError:
            self.stdout.write(self.style.ERROR(f"Could not find file at: {file_path}"))
            return
        except Exception as e:
            self.stdout.write(self.style.ERROR(f"Error seeding workouts: {e}"))
            import traceback

            self.stdout.write(traceback.format_exc())
            return

        self.stdout.write(self.style.SUCCESS("Workout Demo Environment Ready"))
