import json
import os

from django.core.management.base import BaseCommand

from apps.biology.models import (
    AnatomicalDirection,
    Joint,
    JointAction,
    MovementPattern,
    Muscle,
    MuscleGroup,
    MuscleInvolvement,
    MuscleRole,
    PlaneOfMotion,
)


class Command(BaseCommand):
    """Management command to seed biology lookup tables and relational data.

    This command reads a JSON file containing biomechanical data (planes,
    directions, joints, muscles, etc.) and populates the database using
    update_or_create logic to ensure idempotency.
    """

    help = "Seeds biology lookup tables and joint/muscle relational data"

    def handle(self, *args, **kwargs):
        """Executes the seeding logic by parsing the local JSON data file.

        Args:
            *args: Variable length argument list.
            **kwargs: Arbitrary keyword arguments.
        """
        base_dir = os.path.dirname(__file__)
        file_path = os.path.join(base_dir, "seed_biology_data.json")
        objects_written = 0

        try:
            with open(file_path) as f:
                data = json.load(f)
                self.stdout.write("Seeding Biology Data...")

            # --- Simple lookup table population ---

            for item in data.get("planes_of_motion", []):
                _, created = PlaneOfMotion.objects.update_or_create(
                    code=item["code"], defaults={"label": item["label"]}
                )
                if created:
                    self.stdout.write(f"    Created PlaneOfMotion: {item['label']}")
                    objects_written += 1

            for item in data.get("anatomical_directions", []):
                _, created = AnatomicalDirection.objects.update_or_create(
                    code=item["code"], defaults={"label": item["label"]}
                )
                if created:
                    self.stdout.write(
                        f"    Created AnatomicalDirection: {item['label']}"
                    )
                    objects_written += 1

            for item in data.get("movement_patterns", []):
                _, created = MovementPattern.objects.update_or_create(
                    code=item["code"], defaults={"label": item["label"]}
                )
                if created:
                    self.stdout.write(f"    Created MovementPattern: {item['label']}")
                    objects_written += 1

            for item in data.get("joints", []):
                _, created = Joint.objects.update_or_create(
                    code=item["code"], defaults={"label": item["label"]}
                )
                if created:
                    self.stdout.write(f"    Created Joint: {item['label']}")
                    objects_written += 1

            for item in data.get("muscle_roles", []):
                _, created = MuscleRole.objects.update_or_create(
                    code=item["code"], defaults={"label": item["label"]}
                )
                if created:
                    self.stdout.write(f"    Created MuscleRole: {item['label']}")
                    objects_written += 1

            for item in data.get("muscle_groups", []):
                _, created = MuscleGroup.objects.update_or_create(
                    code=item["code"], defaults={"label": item["label"]}
                )
                if created:
                    self.stdout.write(f"    Created MuscleGroup: {item['label']}")
                    objects_written += 1

            # --- Muscles (requires resolving foreign keys for direction and group) ---

            for item in data.get("muscles", []):
                direction = AnatomicalDirection.objects.get(code=item["direction"])
                group = MuscleGroup.objects.get(code=item["group"])
                _, created = Muscle.objects.update_or_create(
                    code=item["code"],
                    defaults={
                        "label": item["label"],
                        "anatomical_direction": direction,
                        "muscle_group": group,
                    },
                )
                if created:
                    self.stdout.write(f"    Created Muscle: {item['label']}")
                    objects_written += 1

            # --- Joint actions and their respective muscle involvements ---

            for action_data in data.get("joint_actions", []):
                joint = Joint.objects.get(code=action_data["joint"])
                movement = MovementPattern.objects.get(code=action_data["movement"])
                plane = PlaneOfMotion.objects.get(code=action_data["plane"])

                joint_action, ja_created = JointAction.objects.get_or_create(
                    joint=joint, movement=movement, plane=plane
                )
                if ja_created:
                    self.stdout.write(
                        f"    Created JointAction: {joint.label} {movement.label}"
                    )
                    objects_written += 1

                for m_data in action_data.get("muscles", []):
                    muscle = Muscle.objects.get(code=m_data["code"])
                    role = MuscleRole.objects.get(code=m_data["role"])
                    _, mi_created = MuscleInvolvement.objects.update_or_create(
                        muscle=muscle,
                        joint_action=joint_action,
                        defaults={
                            "role": role,
                            "impact_factor": m_data["impact"],
                        },
                    )
                    if mi_created:
                        self.stdout.write(
                            f"        Created MuscleInvolvement: {muscle.label}"
                        )
                        objects_written += 1

        except FileNotFoundError:
            self.stdout.write(self.style.ERROR(f"Could not find file at: {file_path}"))
            return
        except Exception as e:
            self.stdout.write(self.style.ERROR(f"Error seeding biology: {e}"))
            return

        self.stdout.write(
            self.style.SUCCESS(
                f"Biology seeded successfully. Objects created: {objects_written}"
            )
        )
