from django.contrib import admin

from core.admin import NormalisedLookupAdmin

from .models import ExperienceLevel, MembershipStatus, TrainingGoal


@admin.register(TrainingGoal)
class TrainingGoalAdmin(NormalisedLookupAdmin):
    """Admin interface for the TrainingGoal model.

    Inherits from NormalisedLookupAdmin to provide standardized lookup
    and normalization functionality for training goals.
    """

    pass


@admin.register(ExperienceLevel)
class ExperienceLevelAdmin(NormalisedLookupAdmin):
    """Admin interface for the ExperienceLevel model.

    Inherits from NormalisedLookupAdmin to provide standardized lookup
    and normalization functionality for experience levels.
    """

    pass


@admin.register(MembershipStatus)
class MembershipStatusAdmin(NormalisedLookupAdmin):
    """Admin interface for the MembershipStatus model.

    Inherits from NormalisedLookupAdmin to provide standardized lookup
    and normalization functionality for membership statuses.
    """

    pass
