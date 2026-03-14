import django_filters

from apps.biology.models import AnatomicalDirection
from apps.users.models import ExperienceLevel

from .models import Exercise


class ExerciseFilter(django_filters.FilterSet):
    target_muscle = django_filters.UUIDFilter(method="filter_target_muscle")

    experience_level = django_filters.ModelMultipleChoiceFilter(
        queryset=ExperienceLevel.objects.all(),
        field_name="experience_level",
    )

    # Equipment

    def filter_target_muscle(self, queryset, name, value):
        return queryset.filter(
            exercise_movements__joint_contributions__joint_action__muscles__muscle=value,
            exercise_movements__joint_contributions__joint_action__muscles__role__role_name__iexact="Agonist",
        ).distinct()

    class Meta:
        model = Exercise

        fields = ["experience_level", "target_muscle"]
