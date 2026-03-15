from django.core.management import call_command
from django.core.management.base import BaseCommand


class Command(BaseCommand):
    help = "Master command — seeds all lookup tables across the application"

    def handle(self, *args, **kwargs):
        self.stdout.write(self.style.MIGRATE_HEADING("Starting Database Seeding..."))

        seed_commands = [
            "seed_users",
            "seed_programs",
            "seed_biology",
            "seed_exercises",
        ]

        for command_name in seed_commands:
            try:
                self.stdout.write(f"\nRunning {command_name}...")
                call_command(command_name)
                self.stdout.write(self.style.SUCCESS(f"{command_name} completed"))
            except Exception as e:
                self.stderr.write(self.style.ERROR(f"{command_name} failed: {e}"))

        self.stdout.write(self.style.SUCCESS("\nDatabase seeded successfully!"))
