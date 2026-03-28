from django.contrib import admin

from .models import ExerciseSessionSnapshot


@admin.register(ExerciseSessionSnapshot)
class ExerciseSessionSnapshotAdmin(admin.ModelAdmin):
    """Admin interface for the ExerciseSessionSnapshot model.

    This class defines the administrative representation of exercise session
    snapshots, ensuring that computed analytics such as 1RM and session loads
    are displayed correctly and kept read-only to preserve data integrity.
    """

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

    # Metrics computed by the snapshot service should not be manually edited.
    readonly_fields = (
        "one_rep_max",
        "session_load",
        "target_load",
        "weight_floor",
        "weight_ceiling",
        "computed_at",
    )
