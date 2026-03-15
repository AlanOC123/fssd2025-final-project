import json
import os

from django.core.management import BaseCommand

from apps.programs.models import (
    ProgramPhaseOption,
    ProgramPhaseStatusOption,
    ProgramStatusOption,
)


class Command(BaseCommand):
    help = "Seeds programs lookup tables: statuses and phase options"

    def handle(self, *args, **options):
        base_dir = os.path.dirname(__file__)
        file_path = os.path.join(base_dir, "seed_programs_data.json")
        objects_written = 0

        try:
            with open(file_path) as f:
                data = json.load(f)
                self.stdout.write("Seeding Programs lookup tables...")

            for item in data.get("program_statuses", []):
                _, created = ProgramStatusOption.objects.update_or_create(
                    code=item["code"],
                    defaults={"label": item["label"]},
                )
                if created:
                    self.stdout.write(f"    Created ProgramStatus: {item['label']}")
                    objects_written += 1

            for item in data.get("phase_statuses", []):
                _, created = ProgramPhaseStatusOption.objects.update_or_create(
                    code=item["code"],
                    defaults={"label": item["label"]},
                )
                if created:
                    self.stdout.write(f"    Created PhaseStatus: {item['label']}")
                    objects_written += 1

            for item in data.get("phase_options", []):
                _, created = ProgramPhaseOption.objects.update_or_create(
                    code=item["code"],
                    defaults={
                        "label": item["label"],
                        "default_duration_days": item["default_duration_days"],
                        "description": item.get("description", ""),
                    },
                )
                if created:
                    self.stdout.write(f"    Created PhaseOption: {item['label']}")
                    objects_written += 1

        except FileNotFoundError:
            self.stdout.write(self.style.ERROR(f"Could not find file at: {file_path}"))
            return

        self.stdout.write(
            self.style.SUCCESS(
                f"Programs seeded successfully. Objects created: {objects_written}"
            )
        )
