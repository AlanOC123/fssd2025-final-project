import django_filters

from .models import Exercise


class ExerciseFilter(django_filters.FilterSet):
    target_muscle = django_filters.UUIDFilter(method="filter_target_muscle")

    direction = django_filters.UUIDFilter(
        field_name="exercise_movements__joint_contributions__joint_action__muscles__muscle__anatomical_direction"
    )

    role = django_filters.UUIDFilter(
        field_name="exercise_movements__joint_contributions__joint_action__muscles__role"
    )

    def filter_target_muscle(self, queryset, name, value):
        return queryset.filter(
            exercise_movements__joint_contributions__joint_action__muscles__muscle__id=value,
            exercise_movements__joint_contributions__joint_action__muscles__role__role_name__iexact="Agonist",
        ).distinct()

    class Meta:
        model = Exercise

        fields = ["equipment", "experience_level", "target_muscle", "direction", "role"]
