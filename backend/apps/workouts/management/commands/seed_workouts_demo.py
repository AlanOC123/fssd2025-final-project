import json
import os
import random
from datetime import datetime, timedelta  # Import standard datetime

from django.contrib.auth import get_user_model
from django.core.management.base import BaseCommand
from django.utils import timezone
from django.utils.timezone import make_aware  # Import make_aware

from apps.exercises.models import Exercise
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
    help = "Seeds workouts based on program phases (History & Future)"

    def handle(self, *args, **kwargs):
        base_dir = os.path.dirname(__file__)
        file_path = os.path.join(base_dir, "seed_workouts_demo_data.json")

        try:
            with open(file_path) as f:
                data = json.load(f)
                self.stdout.write("🏋️  Seeding Workout Demo Data...")

                # Fetch Program and Client
                try:
                    client = User.objects.get(email=data["client_email"])
                    program = Program.objects.get(
                        program_name=data["program_name"],
                        trainer_client_membership__client__user=client,
                    )
                except Exception as e:
                    self.stdout.write(self.style.ERROR(f"Setup Error: {e}"))
                    return

                # Process Phases
                phases = program.phases.all()

                for phase in phases:
                    phase_name = phase.phase_option.phase_name

                    if phase_name not in data["routines"]:
                        self.stdout.write(
                            f"    ℹ️  Skipping phase '{phase_name}' (No routine data)"
                        )
                        continue

                    routine_config = data["routines"][phase_name]
                    self.stdout.write(
                        f"Processing Phase: {phase_name} ({phase.custom_duration} weeks)"
                    )

                    # Calculate Dates
                    today = timezone.now().date()

                    if phase.is_completed and phase.completed_at:
                        end_date = phase.completed_at.date()
                        start_date = end_date - timedelta(weeks=phase.custom_duration)
                    elif phase.is_active:
                        start_date = today - timedelta(days=7)
                        end_date = start_date + timedelta(weeks=phase.custom_duration)
                    else:
                        continue

                    # Generate Workouts
                    current_date = start_date
                    workouts_list = routine_config["workouts"]
                    schedule_days = routine_config["schedule"]

                    workout_idx_cycler = 0

                    while current_date < end_date:
                        if current_date.weekday() in schedule_days:
                            workout_template = workouts_list[
                                workout_idx_cycler % len(workouts_list)
                            ]
                            workout_idx_cycler += 1

                            weeks_in = (current_date - start_date).days // 7
                            overload = weeks_in * 1.25

                            workout = Workout.objects.create(
                                workout_name=f"{workout_template['name']}\
                                    - Week {weeks_in + 1}",
                                estimated_duration_s=3600,
                                program_phase=phase,
                                scheduled_for=current_date,
                            )

                            is_past = current_date < today

                            if is_past:
                                # Make the datetime timezone aware
                                # (USE_TZ=True set in settings.py)
                                naive_dt = datetime.combine(
                                    current_date, datetime.min.time()
                                )
                                aware_dt = make_aware(naive_dt)

                                WorkoutCompletionRecord.objects.create(
                                    workout=workout,
                                    time_taken_s=3600 + random.randint(-200, 200),
                                    completed_at=aware_dt,
                                    is_skipped=False,
                                )

                            for idx, ex_data in enumerate(
                                workout_template["exercises"]
                            ):
                                try:
                                    ex_obj = Exercise.objects.get(
                                        exercise_name=ex_data["name"]
                                    )
                                except Exercise.DoesNotExist:
                                    ex_obj = Exercise.objects.filter(
                                        exercise_name__icontains=ex_data[
                                            "name"
                                        ].split()[0]
                                    ).first()
                                    if not ex_obj:
                                        continue

                                w_exercise = WorkoutExercise.objects.create(
                                    workout=workout,
                                    exercise=ex_obj,
                                    order=idx + 1,
                                    sets_prescribed=ex_data["sets"],
                                )

                                w_ex_log = None
                                if is_past:
                                    naive_dt = datetime.combine(
                                        current_date, datetime.min.time()
                                    )
                                    aware_dt = make_aware(naive_dt)

                                    w_ex_log = (
                                        WorkoutExerciseCompletionRecord.objects.create(
                                            workout_exercise=w_exercise,
                                            completed_at=aware_dt,
                                            difficulty_rating=ex_data["rpe"]
                                            + random.choice([-1, 0, 1]),
                                        )
                                    )

                                target_weight = ex_data["start_weight"] + overload

                                for s in range(ex_data["sets"]):
                                    w_set = WorkoutSet.objects.create(
                                        workout_exercise=w_exercise,
                                        set_order=s + 1,
                                        reps_prescribed=ex_data["reps"],
                                        weight_prescribed=target_weight,
                                    )

                                    if is_past and w_ex_log:
                                        reps_done = ex_data["reps"]
                                        if random.random() > 0.9:
                                            reps_done -= 1

                                        naive_dt = datetime.combine(
                                            current_date, datetime.min.time()
                                        )
                                        aware_dt = make_aware(naive_dt)

                                        WorkoutSetCompletionRecord.objects.create(
                                            workout_set=w_set,
                                            workout_in_progress_record=w_ex_log,
                                            reps_completed=reps_done,
                                            weight_completed=target_weight,
                                            reps_in_reserve=random.choice([1, 2]),
                                            completed_at=aware_dt,
                                        )

                        current_date += timedelta(days=1)

                    self.stdout.write(f"      -> Generated schedule for {phase_name}")

        except FileNotFoundError:
            self.stdout.write(self.style.ERROR(f"Could not find file at: {file_path}"))
        except Exception as e:
            self.stdout.write(self.style.ERROR(f"Error seeding workouts: {e}"))
            import traceback

            self.stdout.write(traceback.format_exc())

        self.stdout.write(self.style.SUCCESS("Workout Demo Environment Ready"))
