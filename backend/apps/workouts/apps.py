from django.apps import AppConfig


class WorkoutsConfig(AppConfig):
    """Configuration class for the Workouts Django application.

    This class handles the metadata and setup configuration for the
    workouts app within the Django project.

    Attributes:
        default_auto_field: Specifies the type of auto-incrementing primary key
            to use for models in this app.
        name: The full Python path to the application.
    """

    default_auto_field = "django.db.models.BigAutoField"
    name = "apps.workouts"
