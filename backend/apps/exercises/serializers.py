from apps.users.serializers import ExperienceLevelSerializer
from core.serializers import (
    ApexSerializer,
    LabelLookupSerializer,
)

from .models import (
    Equipment,
    Exercise,
)


class EquipmentSerializer(LabelLookupSerializer):
    """Serializer for Equipment models.

    Inherits from LabelLookupSerializer to provide standard label and code fields.
    """

    class Meta(LabelLookupSerializer.Meta):
        model = Equipment


class ExerciseSerializer(ApexSerializer):
    """Serializer for the Exercise model.

    Provides a comprehensive representation of an exercise, including nested
    serialization for experience levels and equipment requirements.

    Attributes:
        experience_level: Nested ExperienceLevelSerializer for read-only access.
        equipment: Nested list of EquipmentSerializer for read-only access.
    """

    experience_level = ExperienceLevelSerializer(read_only=True)

    equipment = EquipmentSerializer(read_only=True, many=True)

    class Meta(ApexSerializer.Meta):
        model = Exercise
        fields = ApexSerializer.Meta.fields + [
            "exercise_name",
            "equipment",
            "experience_level",
            "instructions",
            "safety_tips",
        ]
        read_only_fields = fields
