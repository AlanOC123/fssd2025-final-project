from django.contrib import admin

from core.admin import NormalisedLookupAdmin

from .models import ExperienceLevel, MembershipStatus, TrainingGoal


# Register your models here.
@admin.register(TrainingGoal)
class TrainingGoalAdmin(NormalisedLookupAdmin):
    pass


@admin.register(ExperienceLevel)
class ExperienceLevelAdmin(NormalisedLookupAdmin):
    pass


@admin.register(MembershipStatus)
class MembershipStatusAdmin(NormalisedLookupAdmin):
    pass
