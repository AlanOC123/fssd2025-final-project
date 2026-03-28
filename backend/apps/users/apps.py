from django.apps import AppConfig


class UsersConfig(AppConfig):
    """Configuration class for the users application.

    This class handles the initialization of the users app, including
    setting the default primary key type and connecting signal handlers.
    """

    default_auto_field = "django.db.models.BigAutoField"
    name = "apps.users"

    def ready(self):
        """Initializes the application once it is fully loaded.

        This method is used to import signal handlers to ensure they are
        registered with Django's signal dispatcher.
        """
        # Import signals to ensure they are registered when the app is ready.
        # noqa Exception. Needs import but not used.
        import apps.users.signals  # noqa: F401
