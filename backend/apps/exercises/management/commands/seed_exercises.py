import json
import os

from django.core.management.base import BaseCommand

from apps.biology.models import Joint, JointAction
from apps.exercises.models import (
    Exercise,
    ExerciseMovement,
    ExercisePhase,
    JointContribution,
    JointRangeOfMotion,
)
from apps.users.models import ExperienceLevel


class Command(BaseCommand):
    help = "Seeds vital exercise data into the database"

    def handle(self, *args, **kwargs):

        base_dir = os.path.dirname(__file__)
        file_path = os.path.join(base_dir, "seed_exercises_data.json")
        objects_written = 0

        try:
            with open(file_path) as f:
                # Read data from disk
                data = json.load(f)
                self.stdout.write("Seeding Exercises & Biomechanics...")

                # Base Lookup Data

                # Exercise Phases
                for phase_data in data.get("phases", []):
                    # Create the phase instance
                    _, created = ExercisePhase.objects.get_or_create(
                        phase_name=phase_data
                    )

                    # Check if created and increase object total if so
                    if created:
                        self.stdout.write(f"    Created: {phase_data}")
                        objects_written += 1

                # Complex Lookup Data

                # Range of Motion

                for rom_data in data.get("ranges_of_motion", []):
                    # Get the constructor data
                    rom_name = rom_data["name"]
                    impact_factor = rom_data["impact"]

                    # Default allows unique key to rom_name avoiding impact factor
                    # changes creating duplicates on changes
                    # Used update or create to experiment with impact factors
                    rom_obj, created = JointRangeOfMotion.objects.update_or_create(
                        range_of_motion_name=rom_name,
                        defaults={"impact_factor": impact_factor},
                    )

                    if created:
                        self.stdout.write(f"    Created: {rom_obj}")
                        objects_written += 1

                # Exercises
                for exercise_data in data.get("exercises", []):
                    #  Get the base constructor data
                    exercise_name = exercise_data["name"]
                    api_name = exercise_data["api_name"]
                    level_key = exercise_data["level"]

                    # Get the Level from the Database (User Seeding needs to happen)
                    try:
                        level_obj = ExperienceLevel.objects.get(level_name=level_key)
                    except ExperienceLevel.DoesNotExist:
                        raise ValueError(f"Experience Level\
                                '{level_key}' does not exist in DB.")
                    # Create and capture the exercise
                    # Exercise name is the unique value
                    exercise_obj, ex_created = Exercise.objects.get_or_create(
                        exercise_name=exercise_name,
                        defaults={
                            "api_name": api_name,
                            "experience_level": level_obj,
                            "is_enriched": False,
                        },
                    )

                    # If created, log it
                    if ex_created:
                        self.stdout.write(f"    Created: {exercise_obj}")
                        objects_written += 1

                    # Check the exercise has movements attached
                    if "movements" in exercise_data:

                        # Iterate through the movements
                        for movement_data in exercise_data["movements"]:
                            # First create the movement
                            phase_key = movement_data["phase"]

                            try:
                                phase_obj = ExercisePhase.objects.get(
                                    phase_name=phase_key
                                )
                            except ExercisePhase.DoesNotExist:
                                raise ValueError(
                                    f"TYPO ALERT: Phase '{phase_key}' is not valid."
                                )

                            movement_obj, mv_created = (
                                ExerciseMovement.objects.get_or_create(
                                    phase=phase_obj, exercise=exercise_obj
                                )
                            )

                            if mv_created:
                                self.stdout.write(f"    Created: {movement_obj}")
                                objects_written += 1

                            # Check if the movements lists the joint contributions
                            if "contributions" in movement_data:

                                # Iterate over the contributions
                                for contribution_data in movement_data["contributions"]:
                                    joint_key = contribution_data["joint"]
                                    joint_action_key = contribution_data["action"]
                                    joint_rom_key = contribution_data["rom"]

                                    try:
                                        joint_obj = Joint.objects.get(
                                            joint_name=joint_key
                                        )
                                    except Joint.DoesNotExist:
                                        raise ValueError(
                                            f"TYPO ALERT: Joint '{joint_key}'\
                                                not found (Exercise: {exercise_name})"
                                        )

                                    # Filter returns multiple, get the first
                                    joint_action_obj = JointAction.objects.filter(
                                        joint=joint_obj,
                                        movement__pattern_name=joint_action_key,
                                    ).first()

                                    if not joint_action_obj:
                                        raise ValueError(
                                            f"BIOMECHANICS ERROR: '{joint_key}'\
                                                cannot perform '{joint_action_key}'. " f"Check seed_biology_data.json\
                                                or fix typo in {exercise_name}."
                                        )

                                    try:
                                        joint_rom_obj = JointRangeOfMotion.objects.get(
                                            range_of_motion_name=joint_rom_key
                                        )
                                    except JointRangeOfMotion.DoesNotExist:
                                        raise ValueError(f"TYPO ALERT: ROM' \
                                                {joint_rom_key}' not valid.")

                                    contrib_obj, cb_created = (
                                        JointContribution.objects.get_or_create(
                                            joint_action=joint_action_obj,
                                            joint_range_of_motion=joint_rom_obj,
                                            exercise_movement=movement_obj,
                                        )
                                    )

                                    if cb_created:
                                        self.stdout.write(f"    Created: {contrib_obj}")
                                        objects_written += 1

        except FileNotFoundError:
            self.stdout.write(self.style.ERROR(f"Could not find file at: {file_path}"))
        except Exception as e:
            self.stdout.write(self.style.ERROR(f"Error seeding exercises: {e}"))

        self.stdout.write(
            self.style.SUCCESS(f"Exercise App seeded successfully. {objects_written}")
        )
