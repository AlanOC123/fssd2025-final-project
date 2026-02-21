from typing import Any

from django.core.management import call_command
from django.core.management.base import BaseCommand
from django.db import connection


class Command(BaseCommand):
    help = "Master command to trigger all sub demo commands across the application"

    def handle(self, *args, **kwargs):
        self.stdout.write(
            self.style.MIGRATE_HEADING("Starting Demo Enviornment Seeding...")
        )

        seed_commands = [
            "seed_users_demo",
            "seed_programs_demo",
            "seed_workouts_demo",
        ]

        for command_name in seed_commands:
            try:
                self.stdout.write(f"Running {command_name}...")
                call_command(command_name)
                self.stdout.write(
                    self.style.SUCCESS(f"{command_name} completed successfully")
                )
            except Exception as e:
                self.stderr.write(
                    self.style.ERROR(f"Failed to run {command_name}. Error: {e}")
                )

        self.stdout.write(self.style.SUCCESS("Successfully seeded demo environment!"))
