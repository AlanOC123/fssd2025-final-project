from django.contrib import admin

from core.admin import NormalisedLookupAdmin

from .models import (
    AnatomicalDirection,
    Joint,
    JointAction,
    MovementPattern,
    MuscleInvolvement,
    MuscleRole,
    PlaneOfMotion,
)


@admin.register(PlaneOfMotion)
class PlaneOfMotionAdmin(NormalisedLookupAdmin):
    pass


@admin.register(Joint)
class JointAdmin(NormalisedLookupAdmin):
    pass


@admin.register(AnatomicalDirection)
class AnatomicalDirectionAdmin(NormalisedLookupAdmin):
    pass


@admin.register(MovementPattern)
class MovementPatternAdmin(NormalisedLookupAdmin):
    pass


@admin.register(MuscleRole)
class MuscleRoleAdmin(NormalisedLookupAdmin):
    pass


@admin.register(MuscleInvolvement)
class MuscleInvolvementAdmin(admin.ModelAdmin):
    list_display = ("id", "muscle", "joint_action", "role", "impact_factor")
    search_fields = (
        "muscle__label",
        "muscle__code",
        "role__label",
        "role__code",
    )
    ordering = ("-impact_factor",)


@admin.register(JointAction)
class JointActionAdmin(admin.ModelAdmin):
    list_display = ("id", "joint", "movement", "plane")
    search_fields = (
        "joint__label",
        "joint__code",
        "movement__label",
        "movement__code",
        "plane__label",
        "plane__code",
    )
