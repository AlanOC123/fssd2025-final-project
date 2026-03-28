"""Management command to seed user application lookup tables.

This command populates the database with essential lookup data for
ExperienceLevel, TrainingGoal, and MembershipStatus models from a
local JSON source file.
"""

import json
import os

from django.core.management.base import BaseCommand

from apps.users.models import ExperienceLevel, MembershipStatus, TrainingGoal


class Command(BaseCommand):
    """Management command to seed users app lookup tables.

    Iterates through experience levels, training goals, and membership
    statuses defined in a JSON file and ensures they exist in the
    database using update_or_create logic.
    """

    help = (
        "Seeds users app lookup tables: ExperienceLevel, TrainingGoal, MembershipStatus"
    )

    def handle(self, *args, **options):
        """Executes the seeding process for lookup tables.

        Parses the 'seed_users_data.json' file and populates the database
        with the defined lookup records.

        Args:
            *args: Variable length argument list.
            **options: Arbitrary keyword arguments.

        Raises:
            FileNotFoundError: If the source JSON file is not found at the expected path.
        """
        base_dir = os.path.dirname(__file__)
        file_path = os.path.join(base_dir, "seed_users_data.json")
        objects_written = 0

        try:
            with open(file_path) as f:
                data = json.load(f)
                self.stdout.write("Seeding Users lookup tables...")

            # Seed ExperienceLevel records
            for item in data.get("experience_levels", []):
                _, created = ExperienceLevel.objects.update_or_create(
                    code=item["code"],
                    defaults={
                        "label": item["label"],
                        "progression_cap_percent": item["progression_cap_percent"],
                    },
                )
                if created:
                    self.stdout.write(f"    Created ExperienceLevel: {item['label']}")
                    objects_written += 1

            # Seed TrainingGoal records
            for item in data.get("training_goals", []):
                _, created = TrainingGoal.objects.update_or_create(
                    code=item["code"],
                    defaults={
                        "label": item["label"],
                        "rep_range_min": item["rep_range_min"],
                        "rep_range_max": item["rep_range_max"],
                    },
                )
                if created:
                    self.stdout.write(f"    Created TrainingGoal: {item['label']}")
                    objects_written += 1

            # Seed MembershipStatus records
            for item in data.get("membership_statuses", []):
                _, created = MembershipStatus.objects.update_or_create(
                    code=item["code"],
                    defaults={"label": item["label"]},
                )
                if created:
                    self.stdout.write(f"    Created MembershipStatus: {item['label']}")
                    objects_written += 1

        except FileNotFoundError:
            self.stdout.write(self.style.ERROR(f"Could not find file at: {file_path}"))
            return

        self.stdout.write(
            self.style.SUCCESS(
                f"Users seeded successfully. Objects created: {objects_written}"
            )
        )
