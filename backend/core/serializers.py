from rest_framework.serializers import ModelSerializer

CORE_BASE_FIELDS = ["id", "created_at", "updated_at"]
LOOKUP_BASE_FIELDS = ["code", "label", "order_index", "description"]


class ApexSerializer(ModelSerializer):
    class Meta:
        fields = CORE_BASE_FIELDS
        read_only_fields = CORE_BASE_FIELDS


class NormalisedLookupSerializer(ApexSerializer):
    class Meta(ApexSerializer.Meta):
        fields = CORE_BASE_FIELDS + LOOKUP_BASE_FIELDS
        read_only_fields = fields


class LabelLookupSerializer(ApexSerializer):
    class Meta(ApexSerializer.Meta):
        fields = ["id", "label"]
        read_only_fields = fields
