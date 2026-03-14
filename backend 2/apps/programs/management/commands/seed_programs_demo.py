import json
import os
from datetime import timedelta

from django.contrib.auth import get_user_model
from django.core.management.base import BaseCommand
from django.utils import timezone

from apps.programs.models import Program, ProgramPhase, ProgramPhaseOption

# Import models
from apps.users.models import (
    ClientProfile,
    ExperienceLevel,
    TrainerClientMembership,
    TrainerProfile,
    TrainingGoal,
)

User = get_user_model()


class Command(BaseCommand):
    help = "Seeds a Demo Program linked to the Demo Trainer and Client"

    def handle(self, *args, **kwargs):
        base_dir = os.path.dirname(__file__)
        file_path = os.path.join(base_dir, "seed_programs_demo_data.json")

        try:
            with open(file_path) as f:
                data = json.load(f)
                self.stdout.write("Seeding Program Demo Data...")

                # Find the Membership (The Bridge) ---
                trainer_email = data["trainer_email"]
                client_email = data["client_email"]

                try:
                    trainer_user = User.objects.get(email=trainer_email)
                    client_user = User.objects.get(email=client_email)

                    # Get Profiles
                    t_profile = TrainerProfile.objects.get(user=trainer_user)
                    c_profile = ClientProfile.objects.get(user=client_user)

                    # Find the specific Active Membership
                    membership = TrainerClientMembership.objects.get(
                        trainer=t_profile,
                        client=c_profile,
                        status__status_name="ACTIVE",
                    )
                except Exception as e:
                    self.stdout.write(
                        self.style.ERROR(f"Membership Lookup Failed: {e}")
                    )
                    return

                # Create the Program ---
                prog_data = data["program"]

                # Fetch Lookups
                goal_obj = TrainingGoal.objects.get(goal_name=prog_data["goal"])
                level_obj = ExperienceLevel.objects.get(level_name=prog_data["level"])

                program, created = Program.objects.get_or_create(
                    program_name=prog_data["name"],
                    trainer_client_membership=membership,
                    defaults={"training_goal": goal_obj, "experience_level": level_obj},
                )

                if created:
                    self.stdout.write(f"Created Program: {program.program_name}")
                else:
                    self.stdout.write("Program already exists")

                # Create Phases ---
                # Clear existing phases from idempotency
                program.phases.all().delete()

                for phase_data in data["phases"]:
                    option_name = phase_data["option_name"]

                    try:
                        # Find the template
                        option_obj = ProgramPhaseOption.objects.get(
                            phase_name=option_name
                        )

                        # Handle completion dates
                        completed_at = None
                        if phase_data.get("is_completed"):
                            offset = phase_data.get("completed_at_offset_days", 0)
                            completed_at = timezone.now() - timedelta(days=offset)

                        # Create the Phase Instance
                        phase_obj = ProgramPhase.objects.create(
                            program=program,
                            phase_option=option_obj,
                            custom_duration=phase_data["custom_duration"],
                            is_active=phase_data["is_active"],
                            is_completed=phase_data["is_completed"],
                            completed_at=completed_at,
                        )

                        status = "Active" if phase_data["is_active"] else "Pending"
                        status = "Done" if phase_data["is_completed"] else status

                        self.stdout.write(f"Added Phase: {option_name}\
                                ({phase_data['custom_duration']} weeks) [{status}]")

                    except ProgramPhaseOption.DoesNotExist:
                        self.stdout.write(
                            self.style.ERROR(f"Phase Option '{option_name}' not found.\
                                    Did you run seed_programs?")
                        )

        except FileNotFoundError:
            self.stdout.write(self.style.ERROR(f"Could not find file at: {file_path}"))
        except Exception as e:
            self.stdout.write(self.style.ERROR(f"Error seeding program demo: {e}"))

        self.stdout.write(self.style.SUCCESS("Program Demo Environment Ready!"))
