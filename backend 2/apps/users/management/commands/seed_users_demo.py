import json
import os

from django.contrib.auth import get_user_model
from django.core.management.base import BaseCommand

from apps.users.models import (
    ClientProfile,
    ExperienceLevel,
    MembershipStatus,
    TrainerClientMembership,
    TrainerProfile,
    TrainingGoal,
)

User = get_user_model()


class Command(BaseCommand):
    help = "Seeds a Demo Trainer and Client (both Superusers) and links them."

    def handle(self, *args, **kwargs):
        base_dir = os.path.dirname(__file__)
        file_path = os.path.join(base_dir, "seed_users_demo_data.json")

        try:
            with open(file_path) as f:
                data = json.load(f)
                self.stdout.write("Seeding User Demo Data...")

                # Create Trainer (Superuser) ---
                t_data = data["trainer"]
                t_email = t_data["email"]

                self.stdout.write(f"Seeding Trainer Profile. Email {t_email}")

                # Check if user exists first to avoid crashing on re-runs
                if not User.objects.filter(email=t_data["email"]).exists():
                    trainer_user = User.objects.create_superuser(
                        email=t_data["email"],
                        password=t_data["password"],
                        first_name=t_data["first_name"],
                        last_name=t_data["last_name"],
                        # Custom Role Flag
                        is_trainer=True,
                        is_client=False,
                    )
                    self.stdout.write(f"Created Trainer User: {trainer_user.email}")

                else:
                    trainer_user = User.objects.get(email=t_data["email"])
                    self.stdout.write("Trainer User already exists")

                # Create/Update Trainer Profile
                t_profile, created = TrainerProfile.objects.get_or_create(
                    user=trainer_user, defaults={"company": t_data["company"]}
                )

                # Link Many-to-Many fields (Specialisations)
                if created:
                    for spec in t_data.get("specialisations", []):
                        try:
                            goal = TrainingGoal.objects.get(goal_name=spec)
                            t_profile.specialisations.add(goal)
                        except TrainingGoal.DoesNotExist:
                            pass  # Skip if goal seed data is missing

                    for level in t_data.get("accepted_levels", []):
                        try:
                            lvl = ExperienceLevel.objects.get(level_name=level)
                            t_profile.accepted_experience_levels.add(lvl)
                        except ExperienceLevel.DoesNotExist:
                            pass

                # Create Client (Superuser) ---
                c_data = data["client"]
                c_email = c_data["email"]

                self.stdout.write(f"Seeding Client Profile. Email {c_email}")

                if not User.objects.filter(email=c_data["email"]).exists():
                    client_user = User.objects.create_superuser(
                        email=c_data["email"],
                        password=c_data["password"],
                        first_name=c_data["first_name"],
                        last_name=c_data["last_name"],
                        # Custom Role Flag
                        is_trainer=False,
                        is_client=True,
                    )
                    self.stdout.write(f"Created Client User: {client_user.email}")
                else:
                    client_user = User.objects.get(email=c_data["email"])
                    self.stdout.write("Client User already exists")

                # Resolve Lookups for Profile
                try:
                    goal_obj = TrainingGoal.objects.get(goal_name=c_data["goal"])
                    level_obj = ExperienceLevel.objects.get(level_name=c_data["level"])

                except Exception as e:
                    self.stdout.write(
                        self.style.ERROR(f"Missing Lookup Data (Goal/Level): {e}")
                    )
                    return

                # Create/Update Client Profile
                c_profile, _ = ClientProfile.objects.update_or_create(
                    user=client_user,
                    defaults={"training_goal": goal_obj, "experience_level": level_obj},
                )

                # Create Membership ---
                m_data = data["membership"]

                try:
                    status_obj = MembershipStatus.objects.get(
                        status_name=m_data["status"]
                    )

                    _, created = TrainerClientMembership.objects.get_or_create(
                        trainer=t_profile,
                        client=c_profile,
                        defaults={"status": status_obj},
                    )

                    if created:
                        self.stdout.write(
                            f"Linked Membership: {t_profile} <-> {c_profile}"
                        )
                    else:
                        self.stdout.write("Membership linkage already exists")

                except MembershipStatus.DoesNotExist:
                    self.stdout.write(
                        self.style.ERROR(
                            f"Status '{m_data['status']}' not found in DB."
                        )
                    )

        except FileNotFoundError:
            self.stdout.write(self.style.ERROR(f"Could not find file at: {file_path}"))
        except Exception as e:
            self.stdout.write(self.style.ERROR(f"Error seeding user demo: {e}"))

        self.stdout.write(self.style.SUCCESS("User Demo Environment Ready"))
