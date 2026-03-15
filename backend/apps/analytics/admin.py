from django.contrib import admin

from .models import ExerciseSessionSnapshot


@admin.register(ExerciseSessionSnapshot)
class ExerciseSessionSnapshotAdmin(admin.ModelAdmin):
    list_display = (
        "exercise",
        "program",
        "session",
        "one_rep_max",
        "session_load",
        "target_load",
        "weight_floor",
        "weight_ceiling",
        "computed_at",
    )
    list_filter = ("program", "exercise")
    search_fields = ("exercise__exercise_name", "program__program_name")
    readonly_fields = (
        "one_rep_max",
        "session_load",
        "target_load",
        "weight_floor",
        "weight_ceiling",
        "computed_at",
    )
