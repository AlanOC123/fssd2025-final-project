import json
import os

from django.contrib.auth import get_user_model
from django.core.management.base import BaseCommand
from django.utils import timezone

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
    help = "Seeds demo trainer and client users."

    def handle(self, *args, **kwargs):
        base_dir = os.path.dirname(__file__)
        file_path = os.path.join(base_dir, "seed_users_demo_data.json")

        try:
            with open(file_path) as f:
                data = json.load(f)
            self.stdout.write("Seeding User Demo Data...")

            trainer_profiles = {}

            # ── Trainers ──────────────────────────────────────────────────────
            for t_data in data["trainers"]:
                is_superuser = t_data.get("is_superuser", False)

                if not User.objects.filter(email=t_data["email"]).exists():
                    if is_superuser:
                        trainer_user = User.objects.create_superuser(
                            email=t_data["email"],
                            password=t_data["password"],
                            first_name=t_data["first_name"],
                            last_name=t_data["last_name"],
                            is_trainer=True,
                            is_client=False,
                            is_active=True,
                        )
                    else:
                        trainer_user = User.objects.create_user(
                            email=t_data["email"],
                            password=t_data["password"],
                            first_name=t_data["first_name"],
                            last_name=t_data["last_name"],
                            is_trainer=True,
                            is_client=False,
                            is_active=True
                        )
                    self.stdout.write(f"    Created Trainer: {trainer_user.email}")
                else:
                    trainer_user = User.objects.get(email=t_data["email"])
                    self.stdout.write(f"    Trainer exists: {trainer_user.email}")

                t_profile, _ = TrainerProfile.objects.get_or_create(
                    user=trainer_user,
                    defaults={"company": t_data.get("company", "")},
                )

                for code in t_data.get("accepted_goals", []):
                    try:
                        t_profile.accepted_goals.add(
                            TrainingGoal.objects.get(code=code)
                        )
                    except TrainingGoal.DoesNotExist:
                        self.stdout.write(
                            self.style.WARNING(f"    TrainingGoal '{code}' not found")
                        )

                for code in t_data.get("accepted_levels", []):
                    try:
                        t_profile.accepted_levels.add(
                            ExperienceLevel.objects.get(code=code)
                        )
                    except ExperienceLevel.DoesNotExist:
                        self.stdout.write(
                            self.style.WARNING(
                                f"    ExperienceLevel '{code}' not found"
                            )
                        )

                trainer_profiles[t_data["email"]] = t_profile

            # ── Clients ───────────────────────────────────────────────────────
            for c_data in data["clients"]:
                if not User.objects.filter(email=c_data["email"]).exists():
                    client_user = User.objects.create_user(
                        email=c_data["email"],
                        password=c_data["password"],
                        first_name=c_data["first_name"],
                        last_name=c_data["last_name"],
                        is_trainer=False,
                        is_client=True,
                        is_active=True,
                    )
                    self.stdout.write(f"    Created Client: {client_user.email}")
                else:
                    client_user = User.objects.get(email=c_data["email"])
                    self.stdout.write(f"    Client exists: {client_user.email}")

                try:
                    goal_obj = TrainingGoal.objects.get(code=c_data["goal_code"])
                    level_obj = ExperienceLevel.objects.get(code=c_data["level_code"])
                except (TrainingGoal.DoesNotExist, ExperienceLevel.DoesNotExist) as e:
                    self.stdout.write(self.style.ERROR(f"    Lookup data missing: {e}"))
                    continue

                c_profile, _ = ClientProfile.objects.update_or_create(
                    user=client_user,
                    defaults={"goal": goal_obj, "level": level_obj},
                )

                # ── Membership ─────────────────────────────────────────────
                trainer_email = c_data.get("trainer_email")
                status_code = c_data.get("membership_status")

                if not trainer_email or not status_code:
                    self.stdout.write(f"    No membership for {client_user.email}")
                    continue

                t_profile = trainer_profiles.get(trainer_email)
                if not t_profile:
                    self.stdout.write(
                        self.style.WARNING(
                            f"    Trainer {trainer_email} not found for membership"
                        )
                    )
                    continue

                try:
                    status_obj = MembershipStatus.objects.get(code=status_code)
                except MembershipStatus.DoesNotExist:
                    self.stdout.write(
                        self.style.ERROR(
                            f"    MembershipStatus '{status_code}' not found"
                        )
                    )
                    continue

                now = timezone.now()
                extra = (
                    {"responded_at": now, "started_at": now}
                    if status_code == "ACTIVE"
                    else {}
                )

                _, created = TrainerClientMembership.objects.get_or_create(
                    trainer=t_profile,
                    client=c_profile,
                    defaults={"status": status_obj, **extra},
                )

                if created:
                    self.stdout.write(
                        f"    Created Membership: {trainer_email} <-> {client_user.email} [{status_code}]"
                    )
                else:
                    self.stdout.write(
                        f"    Membership exists: {trainer_email} <-> {client_user.email}"
                    )

        except FileNotFoundError:
            self.stdout.write(self.style.ERROR(f"Could not find file at: {file_path}"))
            return
        except Exception as e:
            self.stdout.write(self.style.ERROR(f"Error seeding user demo: {e}"))
            import traceback

            self.stdout.write(traceback.format_exc())
            return

        self.stdout.write(self.style.SUCCESS("User Demo Environment Ready"))
