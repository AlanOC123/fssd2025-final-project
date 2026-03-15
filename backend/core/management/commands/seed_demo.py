from django.core.management import call_command
from django.core.management.base import BaseCommand


class Command(BaseCommand):
    help = "Master command — seeds a complete demo environment on top of seed_db"

    def handle(self, *args, **kwargs):
        self.stdout.write(
            self.style.MIGRATE_HEADING("Starting Demo Environment Seeding...")
        )

        demo_commands = [
            "seed_users_demo",
            "seed_programs_demo",
            "seed_workouts_demo",
        ]

        for command_name in demo_commands:
            try:
                self.stdout.write(f"\nRunning {command_name}...")
                call_command(command_name)
                self.stdout.write(self.style.SUCCESS(f"{command_name} completed"))
            except Exception as e:
                self.stderr.write(self.style.ERROR(f"{command_name} failed: {e}"))

        self.stdout.write(self.style.SUCCESS("\nDemo environment ready!"))
