from typing import Any

from django.core.management import BaseCommand

from apps.users.models import ExperienceLevel, MembershipStatus, TrainingGoal


class Command(BaseCommand):
    help = "Populates the database with initial look up data"

    def handle(self, *args, **options):
        self.stdout.write("Seeding Database...")

        levels = ["Beginner", "Intermediate", "Advanced", "Elite"]
        goals = ["Strength", "Muscle Gain", "Muscle Endurance", "Recovery"]
        objects_wrote = 0

        membership_statuses = [
            "PENDING_TRAINER_REVIEW",
            "PENDING_CLIENT_CONFIRMATION",
            "ACTIVE",
            "REJECTED",
            "TRAINER_DISSOLVED",
            "CLIENT_DISSOLVED",
        ]

        for level in levels:
            obj, created = ExperienceLevel.objects.get_or_create(level_name=level)

            if created:
                objects_wrote += 1
                self.stdout.write(f"    Created Level:  {level}")

        for goal in goals:
            obj, created = TrainingGoal.objects.get_or_create(goal_name=goal)

            if created:
                objects_wrote += 1
                self.stdout.write(f"     Created Goal:   {goal}")

        for status in membership_statuses:
            obj, created = MembershipStatus.objects.get_or_create(status_name=status)

            if created:
                objects_wrote += 1
                self.stdout.write(f"    Created Level:  {status}")

        self.stdout.write(
            self.style.SUCCESS(
                f"Database seeded successfully. Objects created: {objects_wrote}"
            )
        )
