from allauth.account.adapter import DefaultAccountAdapter


class ApexAccountAdapter(DefaultAccountAdapter):
    """Custom allauth adapter for API-only headless setups.

    This adapter disables template-based redirects and overrides default
    behaviors that assume a traditional Django template-driven frontend.
    """

    def respond_user_inactive(self, request, user):
        """Prevents template redirects for inactive users.

        In a headless API setup, allauth's default template views do not exist.
        Since users are typically activated during registration, this path
        is generally bypassed, but explicitly handled here to prevent errors.

        Args:
            request: The current HTTP request object.
            user: The user instance attempting to log in.
        """
        pass

    def is_open_for_signup(self, request):
        """Determines if the site allows new user registrations.

        Args:
            request: The current HTTP request object.

        Returns:
            bool: Always returns True to allow public signups.
        """
        return True

    def get_email_confirmation_url(self, request, emailconfirmation):
        """Returns the URL for email confirmation.

        Args:
            request: The current HTTP request object.
            emailconfirmation: The email confirmation instance.

        Returns:
            None: This is not used in API-only mode.
        """
        return None

    def send_password_reset_mail(self, user, email, extra_context):
        """Sends a password reset email with a frontend-specific link.

        Constructs a reset URL pointing to the decoupled frontend application
        using parameters provided in the extra_context.

        Args:
            user: The user instance requesting a password reset.
            email: The target email address.
            extra_context: A dictionary containing 'uid' and 'token'.
        """
        from django.conf import settings

        uid = extra_context.get("uid", "")
        token = extra_context.get("token", "")
        reset_url = f"{settings.PASSWORD_RESET_LINK}?uid={uid}&token={token}"
        extra_context["password_reset_url"] = reset_url

        super().send_password_reset_mail(user, email, extra_context)
