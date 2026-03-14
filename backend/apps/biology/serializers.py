from rest_framework import serializers

from core.serializers import NormalisedLookupSerializer

from .models import (
    Muscle,
    MuscleGroup,
)


class MuscleGroupSerializer(NormalisedLookupSerializer):

    class Meta(NormalisedLookupSerializer.Meta):
        model = MuscleGroup


class MuscleSerializer(NormalisedLookupSerializer):
    muscle_group = MuscleGroupSerializer(read_only=True)
    anatomical_direction_id = serializers.UUIDField(
        source="anatomical_direction.id", read_only=True, allow_null=True
    )
    anatomical_direction_label = serializers.CharField(
        source="anatomical_direction.label", read_only=True, allow_null=True
    )

    class Meta(NormalisedLookupSerializer.Meta):
        model = Muscle
        fields = NormalisedLookupSerializer.Meta.fields + [
            "muscle_group",
            "anatomical_direction_id",
            "anatomical_direction_label",
        ]
        read_only_fields = fields
