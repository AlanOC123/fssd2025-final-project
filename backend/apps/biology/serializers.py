from rest_framework import serializers

from core.serializers import NormalisedLookupSerializer

from .models import (
    Muscle,
    MuscleGroup,
)


class MuscleGroupSerializer(NormalisedLookupSerializer):
    """Serializer for the MuscleGroup model.

    Inherits from NormalisedLookupSerializer to provide standard label
    and code representations for muscle groups.
    """

    class Meta(NormalisedLookupSerializer.Meta):
        """Metadata for the MuscleGroupSerializer."""

        model = MuscleGroup


class MuscleSerializer(NormalisedLookupSerializer):
    """Serializer for the Muscle model.

    Handles the representation of individual muscles, including a nested
    representation of the associated muscle group and flattened read-only
    fields for anatomical directions.

    Attributes:
        muscle_group: Nested read-only representation of the MuscleGroup.
        anatomical_direction_id: The UUID of the anatomical direction.
        anatomical_direction_label: The human-readable label of the
            anatomical direction.
    """

    muscle_group = MuscleGroupSerializer(read_only=True)

    # Flattened anatomical direction data for easier consumption by the frontend
    anatomical_direction_id = serializers.UUIDField(
        source="anatomical_direction.id", read_only=True, allow_null=True
    )
    anatomical_direction_label = serializers.CharField(
        source="anatomical_direction.label", read_only=True, allow_null=True
    )

    class Meta(NormalisedLookupSerializer.Meta):
        """Metadata for the MuscleSerializer."""

        model = Muscle
        fields = NormalisedLookupSerializer.Meta.fields + [
            "muscle_group",
            "anatomical_direction_id",
            "anatomical_direction_label",
        ]
        read_only_fields = fields
