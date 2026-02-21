import json
import os

from django.core.management.base import BaseCommand

from apps.biology.models import (
    AnatomicalDirection,
    Joint,
    JointAction,
    MovementPattern,
    Muscle,
    MuscleInvolvement,
    MuscleRole,
    PlaneOfMotion,
)


class Command(BaseCommand):
    help = "Seeds data required for biomechanics app to function"

    def handle(self, *args, **kwargs):

        base_dir = os.path.dirname(__file__)
        file_path = os.path.join(base_dir, "seed_biology_data.json")
        objects_written = 0

        try:
            with open(file_path) as f:
                # Get data from disk
                data = json.load(f)
                self.stdout.write("Seeding Biology Data...")

                # Write basic look ups

                # Planes
                for plane in data.get("planes", []):
                    _, created = PlaneOfMotion.objects.get_or_create(plane_name=plane)
                    if created:
                        self.stdout.write(f"    Created: {plane}")
                        objects_written += 1

                # Directions
                for direction in data.get("directions", []):
                    _, created = AnatomicalDirection.objects.get_or_create(
                        direction_name=direction
                    )
                    if created:
                        self.stdout.write(f"    Created: {direction}")
                        objects_written += 1

                # Movements
                for movement in data.get("movements", []):
                    _, created = MovementPattern.objects.get_or_create(
                        pattern_name=movement
                    )
                    if created:
                        self.stdout.write(f"    Created: {movement}")
                        objects_written += 1

                # Joints
                for joint in data.get("joints", []):
                    _, created = Joint.objects.get_or_create(joint_name=joint)
                    if created:
                        self.stdout.write(f"    Created: {joint}")
                        objects_written += 1

                # Role
                for role in data.get("muscle_roles", []):
                    _, created = MuscleRole.objects.get_or_create(role_name=role)
                    if created:
                        self.stdout.write(f"    Created: {role}")
                        objects_written += 1

                # Complex Relations

                # Muscles
                for muscle_data in data.get("muscles", []):
                    # Get Constructor Data
                    muscle_name = muscle_data["name"]
                    direction_key = muscle_data["direction"]

                    try:
                        # Get relateable objects
                        direction_obj = AnatomicalDirection.objects.get(
                            direction_name=direction_key
                        )

                    except AnatomicalDirection.DoesNotExist:
                        raise ValueError(f"{direction_key} not found in database...")

                    # Create objects
                    _, mu_created = Muscle.objects.get_or_create(
                        muscle_name=muscle_name,
                        defaults={"anatomical_direction": direction_obj},
                    )

                    # Check if new instance created
                    if mu_created:
                        self.stdout.write(f"    Created: {muscle_name}")
                        objects_written += 1

                # Joints
                for action in data.get("joint_actions", []):
                    joint_key = action["joint"]
                    movement_key = action["movement"]
                    plane_key = action["plane"]
                    muscles_involved = action["muscles"]

                    try:
                        joint_obj = Joint.objects.get(joint_name=joint_key)
                        movement_obj = MovementPattern.objects.get(
                            pattern_name=movement_key
                        )
                        plane_obj = PlaneOfMotion.objects.get(plane_name=plane_key)
                    except Joint.DoesNotExist:
                        raise ValueError(f"TYPO ERROR: {joint_key} not found.\
                                        Check seeding data")
                    except MovementPattern.DoesNotExist:
                        raise ValueError(f"TYPO ERROR: {movement_key} not found.\
                                        Check seeding data")
                    except PlaneOfMotion.DoesNotExist:
                        raise ValueError(f"TYPO ERROR: {plane_key} not found.\
                                        Check seeding data")

                    joint_action_obj, ja_created = JointAction.objects.get_or_create(
                        joint=joint_obj, movement=movement_obj, plane=plane_obj
                    )

                    if ja_created:
                        self.stdout.write(f"    Created: {joint_action_obj}")
                        objects_written += 1

                    # Create and connect involvement records
                    for muscle_data in muscles_involved:
                        muscle_key = muscle_data["name"]
                        role_key = muscle_data["role"]
                        impact_factor = muscle_data["impact"]

                        try:
                            muscle_obj = Muscle.objects.get(muscle_name=muscle_key)
                            role_obj = MuscleRole.objects.get(role_name=role_key)
                        except Muscle.DoesNotExist:
                            raise ValueError(f"TYPO ERROR: {muscle_key} not found.\
                                        Check seeding data")
                        except MuscleRole.DoesNotExist:
                            raise ValueError(f"TYPO ERROR: {role_key} not found.\
                                        Check seeding data")

                        muscle_involvement_obj, mi_created = (
                            MuscleInvolvement.objects.get_or_create(
                                muscle=muscle_obj,
                                joint_action=joint_action_obj,
                                defaults={
                                    "role": role_obj,
                                    "impact_factor": impact_factor,
                                },
                            )
                        )

                        if mi_created:
                            self.stdout.write(f"    Created: {muscle_involvement_obj}")
                            objects_written += 1

        except FileNotFoundError:
            self.stdout.write(self.style.ERROR(f"Could not find file at: {file_path}"))
            return

        except Exception as e:
            self.stdout.write(self.style.ERROR(f"Error constructing seed data: {e}"))
            return

        self.stdout.write(
            self.style.SUCCESS(
                f"Biology App seeded successfully. Objects created: {objects_written}"
            )
        )
