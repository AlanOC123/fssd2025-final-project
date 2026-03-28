import json
import os
import time

from django.conf import settings
from django.core.exceptions import ImproperlyConfigured
from django.core.management.base import BaseCommand
from requests import get

from apps.biology.models import Joint, JointAction, MovementPattern
from apps.exercises.models import (
    Equipment,
    Exercise,
    ExerciseMovement,
    ExercisePhase,
    JointContribution,
    JointRangeOfMotion,
)
from apps.users.models import ExperienceLevel


class Command(BaseCommand):
    """Django management command to seed exercise and biomechanical reference data.

    This command orchestrates the population of exercise phases, joint ranges of
    motion, exercises (enriched via API Ninja), equipment, and complex
    biomechanical movement data. It utilizes a local cache to minimize
    redundant API calls.
    """

    help = (
        "Seeds exercise phases, ROM lookups, exercises, and biomechanical movement data"
    )

    def handle(self, *args, **kwargs):
        """Executes the seeding logic for the exercise module.

        Args:
            *args: Positional arguments passed to the command.
            **kwargs: Keyword arguments passed to the command.

        Raises:
            ImproperlyConfigured: If the required NINJA_API_KEY is not in settings.
            ValueError: If referenced lookup data (ExperienceLevel, ExercisePhase,
                Joint, etc.) is missing from the database.
        """
        base_dir = os.path.dirname(__file__)
        file_path = os.path.join(base_dir, "seed_exercises_data.json")
        cache_file_path = os.path.join(base_dir, "enrichment_data.json")
        objects_written = 0

        # Load or initialize the API response cache to minimize external requests.
        api_cache = {}
        if os.path.exists(cache_file_path):
            try:
                with open(cache_file_path) as f:
                    api_cache = json.load(f)
            except json.JSONDecodeError:
                api_cache = {}
        self.stdout.write(f"Loaded {len(api_cache)} exercises from local cache.")

        try:
            with open(file_path) as f:
                data = json.load(f)
                self.stdout.write("Seeding Exercises & Biomechanics...")

            # ── Exercise phases ───────────────────────────────────────────────

            for item in data.get("exercise_phases", []):
                _, created = ExercisePhase.objects.update_or_create(
                    code=item["code"], defaults={"label": item["label"]}
                )
                if created:
                    self.stdout.write(f"    Created ExercisePhase: {item['label']}")
                    objects_written += 1

            # ── Ranges of motion ──────────────────────────────────────────────

            for item in data.get("ranges_of_motion", []):
                _, created = JointRangeOfMotion.objects.update_or_create(
                    code=item["code"],
                    defaults={
                        "label": item["label"],
                        "impact_factor": item["impact"],
                    },
                )
                if created:
                    self.stdout.write(
                        f"    Created JointRangeOfMotion: {item['label']}"
                    )
                    objects_written += 1

            # ── Exercises ─────────────────────────────────────────────────────

            api_key = getattr(settings, "NINJA_API_KEY", None)
            if not api_key:
                raise ImproperlyConfigured("Missing NINJA_API_KEY in settings")

            for exercise_data in data.get("exercises", []):
                exercise_name = exercise_data["name"]
                api_name = exercise_data["api_name"]
                level_code = exercise_data["level"]

                # Fetch supplemental data from API Ninjas with a 2-second delay
                # to respect potential rate limits if not already cached.
                if api_name not in api_cache:
                    self.stdout.write(f"    Fetching from API Ninja: {api_name}")
                    time.sleep(2)

                    response = get(
                        f"https://api.api-ninjas.com/v1/exercises?name={api_name}",
                        headers={"X-Api-Key": api_key},
                    )
                    data_arr = response.json()

                    if not data_arr:
                        raise ValueError(
                            f"API Ninja returned no results for '{api_name}'"
                        )

                    enrichment = data_arr[0]
                    api_cache[api_name] = {
                        "instructions": enrichment.get("instructions", ""),
                        "equipment": enrichment.get("equipments", []),
                        "safety_info": enrichment.get("safety_info", ""),
                    }
                    with open(cache_file_path, "w") as cf:
                        json.dump(api_cache, cf, indent=4)
                    self.stdout.write(self.style.SUCCESS(f"    Cached: {api_name}"))

                cached = api_cache[api_name]

                try:
                    level_obj = ExperienceLevel.objects.get(code=level_code)
                except ExperienceLevel.DoesNotExist:
                    raise ValueError(
                        f"ExperienceLevel '{level_code}' not found — run seed_users first"
                    )

                exercise_obj, ex_created = Exercise.objects.get_or_create(
                    exercise_name=exercise_name,
                    defaults={
                        "api_name": api_name,
                        "experience_level": level_obj,
                        "instructions": cached["instructions"],
                        "safety_tips": cached["safety_info"],
                        "is_enriched": False,
                    },
                )

                for equip_name in cached["equipment"]:
                    equip_obj, equip_created = Equipment.objects.update_or_create(
                        code=equip_name.upper().replace(" ", "_"),
                        defaults={"label": equip_name},
                    )
                    exercise_obj.equipment.add(equip_obj)
                    if equip_created:
                        objects_written += 1

                # Update enrichment status based on presence of API-provided content.
                if exercise_obj.instructions and exercise_obj.safety_tips:
                    exercise_obj.is_enriched = True
                exercise_obj.save()

                if ex_created:
                    self.stdout.write(f"    Created Exercise: {exercise_name}")
                    objects_written += 1

                # ── Movements + joint contributions ───────────────────────────

                for movement_data in exercise_data.get("movements", []):
                    phase_code = movement_data["phase"]

                    try:
                        phase_obj = ExercisePhase.objects.get(code=phase_code)
                    except ExercisePhase.DoesNotExist:
                        raise ValueError(f"ExercisePhase '{phase_code}' not found")

                    movement_obj, mv_created = ExerciseMovement.objects.get_or_create(
                        phase=phase_obj, exercise=exercise_obj
                    )
                    if mv_created:
                        self.stdout.write(
                            f"        Created ExerciseMovement: {phase_obj.label} of {exercise_name}"
                        )
                        objects_written += 1

                    for contrib_data in movement_data.get("contributions", []):
                        joint_code = contrib_data["joint"]
                        action_code = contrib_data["action"]
                        rom_code = contrib_data["rom"]

                        try:
                            joint_obj = Joint.objects.get(code=joint_code)
                        except Joint.DoesNotExist:
                            raise ValueError(f"Joint '{joint_code}' not found")

                        # Link biomechanical data: Joint + MovementPattern -> JointAction.
                        movement_pattern = MovementPattern.objects.get(code=action_code)
                        joint_action_obj = JointAction.objects.filter(
                            joint=joint_obj,
                            movement=movement_pattern,
                        ).first()

                        if not joint_action_obj:
                            raise ValueError(
                                f"No JointAction for {joint_code} → {action_code}. "
                                f"Check seed_biology_data.json."
                            )

                        try:
                            rom_obj = JointRangeOfMotion.objects.get(code=rom_code)
                        except JointRangeOfMotion.DoesNotExist:
                            raise ValueError(
                                f"JointRangeOfMotion '{rom_code}' not found"
                            )

                        _, cb_created = JointContribution.objects.get_or_create(
                            joint_action=joint_action_obj,
                            joint_range_of_motion=rom_obj,
                            exercise_movement=movement_obj,
                        )
                        if cb_created:
                            self.stdout.write(
                                f"            Created JointContribution: {joint_code} {action_code} ({rom_code})"
                            )
                            objects_written += 1

        except FileNotFoundError:
            self.stdout.write(self.style.ERROR(f"Could not find file at: {file_path}"))
            return
        except Exception as e:
            self.stdout.write(self.style.ERROR(f"Error seeding exercises: {e}"))
            return

        self.stdout.write(
            self.style.SUCCESS(
                f"Exercises seeded successfully. Objects created: {objects_written}"
            )
        )
