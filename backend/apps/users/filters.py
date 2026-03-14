import django_filters

from .models import TrainerClientMembership


class TrainerClientMembershipFilter(django_filters.FilterSet):
    status = django_filters.CharFilter(field_name="status__label", lookup_expr="iexact")

    class Meta:
        model = TrainerClientMembership
        fields = ["status"]
