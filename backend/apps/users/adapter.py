from allauth.account.adapter import DefaultAccountAdapter


class ApexAccountAdapter(DefaultAccountAdapter):
    """
    Custom allauth adapter for API-only use.
    Disables template-based redirects that don't exist in a headless setup.
    """

    def respond_user_inactive(self, request, user):
        # In API mode there are no allauth template views to redirect to.
        # is_active is set to True during registration so this path should
        # never be reached — but if it is, do nothing and let dj-rest-auth
        # handle the response.
        pass

    def is_open_for_signup(self, request):
        return True

    def get_email_confirmation_url(self, request, emailconfirmation):
        # Not used in API-only mode
        return None

    def send_password_reset_mail(self, user, email, extra_context):
        # Build the reset URL pointing to our frontend route
        from django.conf import settings

        uid = extra_context.get("uid", "")
        token = extra_context.get("token", "")
        reset_url = f"{settings.PASSWORD_RESET_LINK}?uid={uid}&token={token}"
        extra_context["password_reset_url"] = reset_url
        # Call parent but with our URL already set
        super().send_password_reset_mail(user, email, extra_context)
