from django.contrib import admin

from .models import (
    Workout,
    WorkoutCompletionRecord,
    WorkoutExercise,
    WorkoutExerciseCompletionRecord,
    WorkoutSet,
    WorkoutSetCompletionRecord,
)


@admin.register(Workout)
class WorkoutAdmin(admin.ModelAdmin):
    list_display = ("workout_name", "program_phase", "planned_date")
    search_fields = ("workout_name",)
    list_filter = ("planned_date",)


@admin.register(WorkoutExercise)
class WorkoutExerciseAdmin(admin.ModelAdmin):
    list_display = ("__str__", "order", "sets_prescribed")
    search_fields = ("exercise__exercise_name", "workout__workout_name")


@admin.register(WorkoutSet)
class WorkoutSetAdmin(admin.ModelAdmin):
    list_display = ("__str__", "set_order", "reps_prescribed", "weight_prescribed")


@admin.register(WorkoutCompletionRecord)
class WorkoutCompletionRecordAdmin(admin.ModelAdmin):
    list_display = (
        "__str__",
        "client",
        "is_skipped",
        "started_at",
        "completed_at",
        "duration_s",
    )
    list_filter = ("is_skipped",)
    search_fields = ("client__email", "workout__workout_name")
    readonly_fields = ("duration_s",)


@admin.register(WorkoutExerciseCompletionRecord)
class WorkoutExerciseCompletionRecordAdmin(admin.ModelAdmin):
    list_display = ("__str__", "is_skipped", "started_at", "completed_at")
    list_filter = ("is_skipped",)


@admin.register(WorkoutSetCompletionRecord)
class WorkoutSetCompletionRecordAdmin(admin.ModelAdmin):
    list_display = (
        "__str__",
        "is_skipped",
        "reps_completed",
        "weight_completed",
        "difficulty_rating",
    )
    list_filter = ("is_skipped",)
    readonly_fields = ("reps_diff", "weight_diff")
