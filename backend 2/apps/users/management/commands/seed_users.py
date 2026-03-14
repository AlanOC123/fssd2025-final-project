import json
import os

from django.core.management import BaseCommand

from apps.users.models import ExperienceLevel, MembershipStatus, TrainingGoal


class Command(BaseCommand):
    help = "Populates the database with initial look up data"

    def handle(self, *args, **options):
        base_dir = os.path.dirname(__file__)
        file_path = os.path.join(base_dir, "seed_users_data.json")

        objects_written = 0

        try:
            with open(file_path) as f:
                data = json.load(f)
                self.stdout.write("Seeding Data...")

                for key, values in data.items():

                    for value in values:
                        created = False

                        if key == "experience_level":
                            for value in values:
                                _, created = ExperienceLevel.objects.get_or_create(
                                    level_name=value
                                )

                        elif key == "training_goal":
                            _, created = TrainingGoal.objects.get_or_create(
                                goal_name=value
                            )

                        elif key == "membership_status":
                            _, created = MembershipStatus.objects.get_or_create(
                                status_name=value
                            )

                        if created:
                            self.stdout.write(f"    Created: {value}")
                            objects_written += 1

        except FileNotFoundError:
            self.stdout.write(self.style.ERROR(f"Could not find file at: {file_path}"))

        self.stdout.write(
            self.style.SUCCESS(
                f"Users seeded successfully. Objects created: {objects_written}"
            )
        )
