import json
import os
from datetime import timedelta

from django.contrib.auth import get_user_model
from django.core.management.base import BaseCommand
from django.utils import timezone

from apps.programs.constants import (
    ProgramPhaseStatusesVocabulary,
    ProgramStatusesVocabulary,
)
from apps.programs.models import (
    Program,
    ProgramPhase,
    ProgramPhaseOption,
    ProgramPhaseStatusOption,
    ProgramStatusOption,
)
from apps.users.models import (
    ClientProfile,
    ExperienceLevel,
    TrainerClientMembership,
    TrainerProfile,
    TrainingGoal,
)

User = get_user_model()


class Command(BaseCommand):
    help = "Seeds a demo program linked to the demo trainer and client"

    def handle(self, *args, **kwargs):
        base_dir = os.path.dirname(__file__)
        file_path = os.path.join(base_dir, "seed_programs_demo_data.json")

        try:
            with open(file_path) as f:
                data = json.load(f)
                self.stdout.write("Seeding Program Demo Data...")

            # ── Resolve membership ────────────────────────────────────────────

            try:
                trainer_user = User.objects.get(email=data["trainer_email"])
                client_user = User.objects.get(email=data["client_email"])
                t_profile = TrainerProfile.objects.get(user=trainer_user)
                c_profile = ClientProfile.objects.get(user=client_user)
                membership = TrainerClientMembership.objects.get(
                    trainer=t_profile,
                    client=c_profile,
                    status__code="ACTIVE",
                )
            except Exception as e:
                self.stdout.write(self.style.ERROR(f"Membership lookup failed: {e}"))
                return

            # ── Create program ────────────────────────────────────────────────

            now = timezone.now()
            prog_data = data["program"]

            try:
                goal_obj = TrainingGoal.objects.get(code=prog_data["goal_code"])
                level_obj = ExperienceLevel.objects.get(code=prog_data["level_code"])
            except Exception as e:
                self.stdout.write(
                    self.style.ERROR(f"Lookup data missing: {e} — run seed_users first")
                )
                return

            status_in_progress = ProgramStatusOption.objects.get(
                code=ProgramStatusesVocabulary.IN_PROGRESS
            )

            program, created = Program.objects.get_or_create(
                program_name=prog_data["name"],
                trainer_client_membership=membership,
                defaults={
                    "training_goal": goal_obj,
                    "experience_level": level_obj,
                    "status": status_in_progress,
                    "created_by_trainer": trainer_user,
                    "last_edited_by": trainer_user,
                    "submitted_for_review_at": now,
                    "reviewed_at": now,
                    "started_at": now,
                },
            )

            if created:
                self.stdout.write(f"    Created Program: {program.program_name}")
            else:
                self.stdout.write(f"    Program already exists: {program.program_name}")
                # Clear and rebuild phases for idempotency
                program.phases.all().delete()

            # ── Create phases ─────────────────────────────────────────────────

            today = timezone.localdate()

            for phase_data in data["phases"]:
                option_code = phase_data["option_code"]
                status_code = phase_data["status"]
                duration_days = phase_data["duration_days"]
                seq = phase_data["sequence_order"]

                try:
                    option_obj = ProgramPhaseOption.objects.get(code=option_code)
                except ProgramPhaseOption.DoesNotExist:
                    self.stdout.write(
                        self.style.ERROR(
                            f"ProgramPhaseOption '{option_code}' not found — run seed_programs first"
                        )
                    )
                    continue

                status_obj = ProgramPhaseStatusOption.objects.get(code=status_code)

                # Planned start/end are relative to today and sequence order
                planned_start = today - timedelta(days=28 * (3 - seq))
                planned_end = planned_start + timedelta(days=duration_days)

                # Status-specific timestamps
                actual_start = None
                actual_end = None
                started_at = None
                completed_at = None

                if status_code == ProgramPhaseStatusesVocabulary.COMPLETED:
                    days_ago = phase_data.get("completed_days_ago", 14)
                    actual_start = today - timedelta(days=days_ago + duration_days)
                    actual_end = today - timedelta(days=days_ago)
                    started_at = now - timedelta(days=days_ago + duration_days)
                    completed_at = now - timedelta(days=days_ago)

                elif status_code == ProgramPhaseStatusesVocabulary.ACTIVE:
                    actual_start = today - timedelta(days=7)
                    started_at = now - timedelta(days=7)

                phase_kwargs = dict(
                    program=program,
                    phase_option=option_obj,
                    phase_name=phase_data.get("phase_name", ""),
                    phase_goal=phase_data.get("phase_goal", ""),
                    sequence_order=seq,
                    status=status_obj,
                    planned_start_date=planned_start,
                    planned_end_date=planned_end,
                    created_by_trainer=trainer_user,
                    last_edited_by=trainer_user,
                )

                if actual_start:
                    phase_kwargs["actual_start_date"] = actual_start
                if actual_end:
                    phase_kwargs["actual_end_date"] = actual_end
                if started_at:
                    phase_kwargs["started_at"] = started_at
                if completed_at:
                    phase_kwargs["completed_at"] = completed_at

                if status_code == ProgramPhaseStatusesVocabulary.SKIPPED:
                    phase_kwargs["skipped_at"] = now
                    phase_kwargs["skipped_reason"] = "Demo skip"

                if status_code == ProgramPhaseStatusesVocabulary.ARCHIVED:
                    phase_kwargs["archived_at"] = now
                    phase_kwargs["archived_reason"] = "Demo archive"

                ProgramPhase.objects.create(**phase_kwargs)
                self.stdout.write(
                    f"    Created Phase: {option_obj.label} [{status_code}]"
                )

        except FileNotFoundError:
            self.stdout.write(self.style.ERROR(f"Could not find file at: {file_path}"))
            return
        except Exception as e:
            self.stdout.write(self.style.ERROR(f"Error seeding program demo: {e}"))
            return

        self.stdout.write(self.style.SUCCESS("Program Demo Environment Ready"))
