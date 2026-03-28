from django.apps import AppConfig


class BiologyConfig(AppConfig):
    """Configuration class for the biology application.

    This class defines the metadata and configuration for the biology app,
    including the default auto-incrementing field type and the internal name.
    """

    default_auto_field = "django.db.models.BigAutoField"
    name = "apps.biology"
