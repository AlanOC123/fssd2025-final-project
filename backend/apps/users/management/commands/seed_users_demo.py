import json
import os

from django.contrib.auth import get_user_model
from django.core.management.base import BaseCommand
from django.utils import timezone

from apps.users.constants import MembershipVocabulary
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
    help = "Seeds demo trainer and client users with an active membership."

    def handle(self, *args, **kwargs):
        base_dir = os.path.dirname(__file__)
        file_path = os.path.join(base_dir, "seed_users_demo_data.json")

        try:
            with open(file_path) as f:
                data = json.load(f)
                self.stdout.write("Seeding User Demo Data...")

            # ── Trainer ───────────────────────────────────────────────────────

            t_data = data["trainer"]

            if not User.objects.filter(email=t_data["email"]).exists():
                trainer_user = User.objects.create_superuser(
                    email=t_data["email"],
                    password=t_data["password"],
                    first_name=t_data["first_name"],
                    last_name=t_data["last_name"],
                    is_trainer=True,
                    is_client=False,
                )
                self.stdout.write(f"    Created Trainer: {trainer_user.email}")
            else:
                trainer_user = User.objects.get(email=t_data["email"])
                self.stdout.write(f"    Trainer exists: {trainer_user.email}")

            t_profile, _ = TrainerProfile.objects.get_or_create(
                user=trainer_user,
                defaults={"company": t_data["company"]},
            )

            for code in t_data.get("accepted_goals", []):
                try:
                    t_profile.accepted_goals.add(TrainingGoal.objects.get(code=code))
                except TrainingGoal.DoesNotExist:
                    self.stdout.write(
                        self.style.WARNING(
                            f"    TrainingGoal '{code}' not found — run seed_users first"
                        )
                    )

            for code in t_data.get("accepted_levels", []):
                try:
                    t_profile.accepted_levels.add(
                        ExperienceLevel.objects.get(code=code)
                    )
                except ExperienceLevel.DoesNotExist:
                    self.stdout.write(
                        self.style.WARNING(
                            f"    ExperienceLevel '{code}' not found — run seed_users first"
                        )
                    )

            # ── Client ────────────────────────────────────────────────────────

            c_data = data["client"]

            if not User.objects.filter(email=c_data["email"]).exists():
                client_user = User.objects.create_superuser(
                    email=c_data["email"],
                    password=c_data["password"],
                    first_name=c_data["first_name"],
                    last_name=c_data["last_name"],
                    is_trainer=False,
                    is_client=True,
                )
                self.stdout.write(f"    Created Client: {client_user.email}")
            else:
                client_user = User.objects.get(email=c_data["email"])
                self.stdout.write(f"    Client exists: {client_user.email}")

            try:
                goal_obj = TrainingGoal.objects.get(code=c_data["goal_code"])
                level_obj = ExperienceLevel.objects.get(code=c_data["level_code"])
            except (TrainingGoal.DoesNotExist, ExperienceLevel.DoesNotExist) as e:
                self.stdout.write(
                    self.style.ERROR(f"Lookup data missing: {e} — run seed_users first")
                )
                return

            c_profile, _ = ClientProfile.objects.update_or_create(
                user=client_user,
                defaults={"goal": goal_obj, "level": level_obj},
            )

            # ── Membership ────────────────────────────────────────────────────

            m_data = data["membership"]

            try:
                status_obj = MembershipStatus.objects.get(code=m_data["status_code"])
            except MembershipStatus.DoesNotExist:
                self.stdout.write(
                    self.style.ERROR(
                        f"MembershipStatus '{m_data['status_code']}' not found — run seed_users first"
                    )
                )
                return

            now = timezone.now()
            _, created = TrainerClientMembership.objects.get_or_create(
                trainer=t_profile,
                client=c_profile,
                defaults={
                    "status": status_obj,
                    "responded_at": now,
                    "started_at": now,
                },
            )

            if created:
                self.stdout.write(
                    f"    Created Membership: {t_profile} <-> {c_profile}"
                )
            else:
                self.stdout.write("    Membership already exists")

        except FileNotFoundError:
            self.stdout.write(self.style.ERROR(f"Could not find file at: {file_path}"))
            return
        except Exception as e:
            self.stdout.write(self.style.ERROR(f"Error seeding user demo: {e}"))
            return

        self.stdout.write(self.style.SUCCESS("User Demo Environment Ready"))
