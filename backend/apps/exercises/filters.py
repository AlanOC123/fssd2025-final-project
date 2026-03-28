import django_filters

from apps.biology.constants import MuscleRoleVocabulary

from .models import Exercise


class ExerciseFilter(django_filters.FilterSet):
    """Filter set for Exercise objects allowing filtering by muscle, group, and equipment.

    This filter set provides specialized methods to traverse the complex relationship
    between exercises, movements, joint contributions, and muscle roles to identify
    target muscles (agonists).
    """

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
        """Filters exercises by a specific target muscle ID.

        Args:
            queryset: The initial QuerySet of Exercise objects.
            name: The name of the filter field.
            value: The UUID of the muscle to filter by.

        Returns:
            A QuerySet containing exercises where the specified muscle acts as an agonist.
        """
        # Traverses Exercise -> Movement -> JointContribution -> JointAction -> MuscleLink
        # filtering specifically for muscles with the 'AGONIST' role.
        return queryset.filter(
            exercise_movements__joint_contributions__joint_action__muscles__muscle__id=value,
            exercise_movements__joint_contributions__joint_action__muscles__role__code=MuscleRoleVocabulary.AGONIST,
        ).distinct()

    def filter_target_muscle_label(self, queryset, name, value):
        """Filters exercises by a target muscle's label (case-insensitive partial match).

        Args:
            queryset: The initial QuerySet of Exercise objects.
            name: The name of the filter field.
            value: The string fragment of the muscle label.

        Returns:
            A QuerySet containing exercises where a matching muscle acts as an agonist.
        """
        return queryset.filter(
            exercise_movements__joint_contributions__joint_action__muscles__muscle__label__icontains=value,
            exercise_movements__joint_contributions__joint_action__muscles__role__code=MuscleRoleVocabulary.AGONIST,
        ).distinct()

    def filter_target_muscle_group_id(self, queryset, name, value):
        """Filters exercises by a specific muscle group ID.

        Args:
            queryset: The initial QuerySet of Exercise objects.
            name: The name of the filter field.
            value: The UUID of the muscle group to filter by.

        Returns:
            A QuerySet containing exercises targeting muscles within the specified group.
        """
        return queryset.filter(
            exercise_movements__joint_contributions__joint_action__muscles__muscle__muscle_group__id=value,
            exercise_movements__joint_contributions__joint_action__muscles__role__code=MuscleRoleVocabulary.AGONIST,
        ).distinct()

    def filter_target_muscle_group_label(self, queryset, name, value):
        """Filters exercises by a muscle group's label (case-insensitive partial match).

        Args:
            queryset: The initial QuerySet of Exercise objects.
            name: The name of the filter field.
            value: The string fragment of the muscle group label.

        Returns:
            A QuerySet containing exercises targeting muscles within matching groups.
        """
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
