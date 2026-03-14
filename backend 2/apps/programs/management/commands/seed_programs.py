import json
import os

from django.core.management import BaseCommand

from apps.programs.models import ProgramPhaseOption


class Command(BaseCommand):
    help = "Populates the program slice database with initial look up data"

    def handle(self, *args, **options):
        base_dir = os.path.dirname(__file__)
        file_path = os.path.join(base_dir, "seed_programs_data.json")

        objects_written = 0

        try:
            with open(file_path) as f:
                self.stdout.write("Seeding Programs Lookup Tables...")
                data = json.load(f)

            for option in data["program_phase_options"]:

                obj, created = ProgramPhaseOption.objects.get_or_create(
                    phase_name=option["phase_name"],
                    defaults={
                        "order_index": option["order_index"],
                        "default_duration": option["default_duration"],
                        "description": option["description"],
                    },
                )

                if created:
                    self.stdout.write(f"    Created: {option['phase_name']}")
                    objects_written += 1

        except FileNotFoundError:
            self.stdout.write(self.style.ERROR(f"Could not find file at: {file_path}"))

        self.stdout.write(
            self.style.SUCCESS(
                f"Program App seeded successfully. Objects created: {objects_written}"
            )
        )
