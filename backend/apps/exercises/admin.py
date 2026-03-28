from django.contrib import admin

from .models import (
    Equipment,
    Exercise,
    ExerciseMovement,
    ExercisePhase,
    JointContribution,
    JointRangeOfMotion,
)


@admin.register(Exercise)
class ExerciseAdmin(admin.ModelAdmin):
    """Admin configuration for the Exercise model.

    Provides a list view with basic metrics and search capabilities for
    exercise names and API identifiers.
    """

    list_display = ("exercise_name", "experience_level", "is_enriched")
    search_fields = ("exercise_name", "api_name")
    list_filter = ("experience_level", "is_enriched", "equipment")
    readonly_fields = ("is_enriched",)


@admin.register(Equipment)
class EquipmentAdmin(admin.ModelAdmin):
    """Admin configuration for the Equipment model."""

    list_display = ("label", "code")
    search_fields = ("label", "code")


@admin.register(ExercisePhase)
class ExercisePhaseAdmin(admin.ModelAdmin):
    """Admin configuration for the ExercisePhase model."""

    list_display = ("label", "code")


@admin.register(JointRangeOfMotion)
class JointRangeOfMotionAdmin(admin.ModelAdmin):
    """Admin configuration for the JointRangeOfMotion model.

    Orders entries by their impact factor in descending order.
    """

    list_display = ("label", "code", "impact_factor")
    ordering = ("-impact_factor",)


@admin.register(ExerciseMovement)
class ExerciseMovementAdmin(admin.ModelAdmin):
    """Admin configuration for the ExerciseMovement model.

    Allows searching by the related exercise name.
    """

    list_display = ("exercise", "phase")
    search_fields = ("exercise__exercise_name",)


@admin.register(JointContribution)
class JointContributionAdmin(admin.ModelAdmin):
    """Admin configuration for the JointContribution model."""

    list_display = ("exercise_movement", "joint_action", "joint_range_of_motion")
