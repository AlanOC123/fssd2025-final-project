from django.apps import AppConfig


class ProgramsConfig(AppConfig):
    """Configuration class for the Programs Django application.

    Attributes:
        default_auto_field: The implicit primary key type to use for models.
        name: The full Python path to the application.
    """

    default_auto_field = "django.db.models.BigAutoField"
    name = "apps.programs"


class ProgramStatusesVocabulary:
    """Vocabulary constants for Program status states.

    Defines the lifecycle stages of a program and provides logical groupings
    for state-based filtering and transitions.
    """

    CREATING = "CREATING"
    REVIEW = "OUT_FOR_REVIEW"
    READY = "READY_TO_BEGIN"
    IN_PROGRESS = "IN_PROGRESS"
    COMPLETED = "COMPLETED"
    ABANDONED = "ABANDONED"

    ALL = {CREATING, REVIEW, READY, IN_PROGRESS, COMPLETED, ABANDONED}
    SUBMITTED_STATES = {REVIEW, READY, IN_PROGRESS, COMPLETED, ABANDONED}
    REVIEWED_STATES = {READY, IN_PROGRESS, COMPLETED, ABANDONED}
    STARTED_STATES = {IN_PROGRESS, COMPLETED, ABANDONED}
    LIVE_STATES = {CREATING, REVIEW, READY, IN_PROGRESS}
    FINISHED_STATES = {COMPLETED, ABANDONED}


class ProgramPhaseStatusesVocabulary:
    """Vocabulary constants for ProgramPhase status states.

    Defines the lifecycle stages for individual phases within a program,
    including states for planning, execution, and completion.
    """

    PLANNED = "PLANNED"
    NEXT = "NEXT"
    ACTIVE = "ACTIVE"
    COMPLETED = "COMPLETED"
    SKIPPED = "SKIPPED"
    ARCHIVED = "ARCHIVED"

    ALL = {PLANNED, NEXT, ACTIVE, COMPLETED, SKIPPED, ARCHIVED}
    PRE_ACTIVE_STATES = {PLANNED, NEXT}
    ACTIONABLE_STATES = {NEXT, ACTIVE}
    LIVE_STATES = {PLANNED, NEXT, ACTIVE}
    FINISHED_STATES = {COMPLETED, SKIPPED, ARCHIVED}
