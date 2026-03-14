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
    class Meta(LabelLookupSerializer.Meta):
        model = Equipment


class ExerciseSerializer(ApexSerializer):
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
