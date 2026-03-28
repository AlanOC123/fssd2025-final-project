from django.apps import AppConfig


class AnalyticsConfig(AppConfig):
    """Configuration class for the analytics application.

    This class defines the metadata and settings for the analytics app,
    including the default auto-incrementing primary key field type.
    """

    default_auto_field = "django.db.models.BigAutoField"
    name = "apps.analytics"
