from django.apps import AppConfig


class ProgramsConfig(AppConfig):
    """Configuration class for the Programs Django application.

    Attributes:
        default_auto_field: The implicit primary key type to use for models.
        name: The full Python path to the application.
    """

    default_auto_field = "django.db.models.BigAutoField"
    name = "apps.programs"
