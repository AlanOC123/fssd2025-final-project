import django_filters

from apps.biology.constants import MuscleRoleVocabulary

from .models import Exercise


class ExerciseFilter(django_filters.FilterSet):
    target_muscle_id = django_filters.UUIDFilter(method="filter_target_muscle_id")
    target_muscle_label = django_filters.CharFilter(method="filter_target_muscle_label")

    target_muscle_group_id = django_filters.UUIDFilter(
        method="filter_target_muscle_group_id"
    )
    target_muscle_group_label = django_filters.CharFilter(
        method="filter_target_muscle_group_label"
    )

    experience_level = django_filters.UUIDFilter(field_name="experience_level__id")
    equipment = django_filters.UUIDFilter(field_name="equipment__id")

    def filter_target_muscle_id(self, queryset, name, value):
        return queryset.filter(
            exercise_movements__joint_contributions__joint_action__muscles__muscle__id=value,
            exercise_movements__joint_contributions__joint_action__muscles__role__code=MuscleRoleVocabulary.AGONIST,
        ).distinct()

    def filter_target_muscle_label(self, queryset, name, value):
        return queryset.filter(
            exercise_movements__joint_contributions__joint_action__muscles__muscle__label__icontains=value,
            exercise_movements__joint_contributions__joint_action__muscles__role__code=MuscleRoleVocabulary.AGONIST,
        ).distinct()

    def filter_target_muscle_group_id(self, queryset, name, value):
        return queryset.filter(
            exercise_movements__joint_contributions__joint_action__muscles__muscle__muscle_group__id=value,
            exercise_movements__joint_contributions__joint_action__muscles__role__code=MuscleRoleVocabulary.AGONIST,
        ).distinct()

    def filter_target_muscle_group_label(self, queryset, name, value):
        return queryset.filter(
            exercise_movements__joint_contributions__joint_action__muscles__muscle__muscle_group__label__icontains=value,
            exercise_movements__joint_contributions__joint_action__muscles__role__code=MuscleRoleVocabulary.AGONIST,
        ).distinct()

    class Meta:
        model = Exercise

        fields = [
            "equipment",
            "experience_level",
            "target_muscle_id",
            "target_muscle_label",
            "target_muscle_group_id",
            "target_muscle_group_label",
        ]
