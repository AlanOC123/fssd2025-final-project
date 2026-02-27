class SuperUserRestrictedMixin:
    """
    Mixin that enables a request to only be visible to an authenticated admin.
    Returns an empty array if not authenticated
    """

    def get_queryset(self):
        # Get the user
        user = self.request.user

        # Start with the inital query set, E.G Muscle.objects.all()
        queryset = super().get_queryset()

        # Check if its a superuser making the request
        is_superuser = user.is_superuser

        # Return the query set if so
        if is_superuser:
            return queryset

        # Return an empty array elsewise
        return queryset.none()
