import json
import os

from django.core.management import BaseCommand

from apps.users.models import ExperienceLevel, MembershipStatus, TrainingGoal


class Command(BaseCommand):
    help = (
        "Seeds users app lookup tables: ExperienceLevel, TrainingGoal, MembershipStatus"
    )

    def handle(self, *args, **options):
        base_dir = os.path.dirname(__file__)
        file_path = os.path.join(base_dir, "seed_users_data.json")
        objects_written = 0

        try:
            with open(file_path) as f:
                data = json.load(f)
                self.stdout.write("Seeding Users lookup tables...")

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
