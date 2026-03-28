import django_filters

from .models import TrainerClientMembership


class TrainerClientMembershipFilter(django_filters.FilterSet):
    """Filter set for TrainerClientMembership queries.

    Provides filtering capabilities for membership records, primarily
    enabling case-insensitive filtering by the status label.
    """

    status = django_filters.CharFilter(field_name="status__label", lookup_expr="iexact")

    class Meta:
        """Metadata for the TrainerClientMembershipFilter."""

        model = TrainerClientMembership
        fields = ["status"]
