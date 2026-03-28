import django_filters

from .models import Program


class ProgramFilter(django_filters.FilterSet):
    """Filter set for the Program model.

    Provides filtering capabilities for programs based on status code,
    membership, training goals, and experience levels.

    Attributes:
        status: A character filter for case-insensitive status code matching.
        trainer_client_membership: A UUID filter for specific memberships.
    """

    status = django_filters.CharFilter(field_name="status__code", lookup_expr="iexact")
    trainer_client_membership = django_filters.UUIDFilter(
        field_name="trainer_client_membership"
    )

    class Meta:
        """Metadata options for ProgramFilter."""

        model = Program
        fields = [
            "status",
            "trainer_client_membership",
            "training_goal",
            "experience_level",
        ]
