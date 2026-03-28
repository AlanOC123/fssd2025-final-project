"""URL routing configuration for the biology application.

This module defines the API endpoints for muscle and muscle group resources
using a RESTful router.
"""

from django.urls import include, path
from rest_framework.routers import DefaultRouter

from .views import MuscleGroupViewSet, MuscleViewSet

# Initialize the standard REST framework router
router = DefaultRouter()

# Register endpoints for biological data
router.register(prefix="muscles", viewset=MuscleViewSet, basename="muscles")
router.register(
    prefix="muscle-groups", viewset=MuscleGroupViewSet, basename="muscle-groups"
)

# Include the router-generated URLs in the application's URL patterns
urlpatterns = [
    path("", include(router.urls)),
]
