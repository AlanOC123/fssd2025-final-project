import django_filters

from .models import Program


class ProgramFilter(django_filters.FilterSet):
    status = django_filters.CharFilter(field_name="status__code", lookup_expr="iexact")
    trainer_client_membership = django_filters.UUIDFilter(
        field_name="trainer_client_membership"
    )

    class Meta:
        model = Program
        fields = [
            "status",
            "trainer_client_membership",
            "training_goal",
            "experience_level",
        ]
