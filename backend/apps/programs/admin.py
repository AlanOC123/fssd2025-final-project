from django.contrib import admin

from .models import (
    Program,
    ProgramPhase,
    ProgramPhaseOption,
    ProgramPhaseStatusOption,
    ProgramStatusOption,
)


@admin.register(ProgramPhaseOption)
class ProgramPhaseOptionAdmin(admin.ModelAdmin):
    """Admin interface configuration for ProgramPhaseOption models.

    Attributes:
        list_display: Fields displayed in the change list view.
        search_fields: Fields used for the search functionality.
    """

    list_display = ("label", "code", "default_duration_days")
    search_fields = ("label", "code")


@admin.register(ProgramStatusOption)
class ProgramStatusOptionAdmin(admin.ModelAdmin):
    """Admin interface configuration for ProgramStatusOption models."""

    list_display = ("label", "code")


@admin.register(ProgramPhaseStatusOption)
class ProgramPhaseStatusOptionAdmin(admin.ModelAdmin):
    """Admin interface configuration for ProgramPhaseStatusOption models."""

    list_display = ("label", "code")


@admin.register(Program)
class ProgramAdmin(admin.ModelAdmin):
    """Admin interface configuration for Program models.

    Attributes:
        list_display: Fields displayed in the change list view.
        list_filter: Fields available for filtering the list.
        search_fields: Fields used for the search functionality.
        readonly_fields: Fields that cannot be edited in the admin UI.
    """

    list_display = (
        "program_name",
        "status",
        "training_goal",
        "experience_level",
        "created_by_trainer",
        "version",
    )
    list_filter = ("status",)
    search_fields = ("program_name",)
    readonly_fields = ("created_at", "updated_at", "version")


@admin.register(ProgramPhase)
class ProgramPhaseAdmin(admin.ModelAdmin):
    """Admin interface configuration for ProgramPhase models.

    Attributes:
        list_display: Fields displayed in the change list view.
        list_filter: Fields available for filtering the list.
        search_fields: Fields used for the search functionality.
        readonly_fields: Fields that cannot be edited in the admin UI.
    """

    list_display = (
        "__str__",
        "status",
        "sequence_order",
        "planned_start_date",
        "planned_end_date",
    )
    list_filter = ("status",)
    search_fields = ("phase_name", "program__program_name")
    readonly_fields = ("created_at", "updated_at")
