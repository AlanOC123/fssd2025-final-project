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
    """Admin interface for managing the PlaneOfMotion model.

    Utilizes the standardized normalization and lookup functionality provided
    by NormalisedLookupAdmin.
    """

    pass


@admin.register(Joint)
class JointAdmin(NormalisedLookupAdmin):
    """Admin interface for managing the Joint model.

    Utilizes the standardized normalization and lookup functionality provided
    by NormalisedLookupAdmin.
    """

    pass


@admin.register(AnatomicalDirection)
class AnatomicalDirectionAdmin(NormalisedLookupAdmin):
    """Admin interface for managing the AnatomicalDirection model.

    Utilizes the standardized normalization and lookup functionality provided
    by NormalisedLookupAdmin.
    """

    pass


@admin.register(MovementPattern)
class MovementPatternAdmin(NormalisedLookupAdmin):
    """Admin interface for managing the MovementPattern model.

    Utilizes the standardized normalization and lookup functionality provided
    by NormalisedLookupAdmin.
    """

    pass


@admin.register(MuscleRole)
class MuscleRoleAdmin(NormalisedLookupAdmin):
    """Admin interface for managing the MuscleRole model.

    Utilizes the standardized normalization and lookup functionality provided
    by NormalisedLookupAdmin.
    """

    pass


@admin.register(MuscleInvolvement)
class MuscleInvolvementAdmin(admin.ModelAdmin):
    """Admin interface for managing muscle involvement in joint actions.

    Exposes the relationship between muscles, their roles, and the calculated
    impact factors for specific joint actions.
    """

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
    """Admin interface for managing anatomical joint actions.

    Provides a view of joint movements and their respective planes of motion.
    """

    list_display = ("id", "joint", "movement", "plane")
    search_fields = (
        "joint__label",
        "joint__code",
        "movement__label",
        "movement__code",
        "plane__label",
        "plane__code",
    )
