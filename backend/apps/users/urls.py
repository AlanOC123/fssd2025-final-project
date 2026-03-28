"""URL routing configuration for the users application.

This module defines the API endpoints for user profiles, experience levels,
training goals, and trainer-client memberships using Django Rest Framework's
DefaultRouter.
"""

from django.urls import include, path
from rest_framework.routers import DefaultRouter

from .views import (
    ClientProfileViewSet,
    ExperienceLevelViewSet,
    TrainerClientMembershipViewSet,
    TrainerMatchingViewSet,
    TrainerProfileViewSet,
    TrainingGoalViewSet,
)

# Initialize the default router for REST API registration
router = DefaultRouter()

# Register lookup and utility endpoints
router.register(
    prefix="experience-levels",
    viewset=ExperienceLevelViewSet,
    basename="experience-levels",
)
router.register(
    prefix="training-goals",
    viewset=TrainingGoalViewSet,
    basename="training-goals",
)

# Register membership and discovery endpoints
router.register(
    prefix="trainer-client-memberships",
    viewset=TrainerClientMembershipViewSet,
    basename="trainer-client-memberships",
)
router.register(
    prefix="find-trainers",
    viewset=TrainerMatchingViewSet,
    basename="find-trainers",
)

# Register role-specific profile management endpoints
router.register(
    prefix="trainer-profile",
    viewset=TrainerProfileViewSet,
    basename="trainer-profile",
)
router.register(
    prefix="client-profile",
    viewset=ClientProfileViewSet,
    basename="client-profile",
)

# Core URL patterns including all routed viewsets
urlpatterns = [
    path("", include(router.urls)),
]
