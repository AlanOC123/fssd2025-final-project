"""URL configuration for the programs application.

Defines the API routes for programs, program phases, and phase options
using a REST framework DefaultRouter to automatically generate URL patterns.
"""

from django.urls import include, path
from rest_framework.routers import DefaultRouter

from apps.programs.views import (
    ProgramPhaseOptionViewSet,
    ProgramPhaseViewSet,
    ProgramViewSet,
)

# Initialize the router and register viewsets for program management.
router = DefaultRouter()
router.register(r"programs", ProgramViewSet, basename="programs")
router.register(r"program-phases", ProgramPhaseViewSet, basename="program-phases")
router.register(
    r"program-phase-options",
    ProgramPhaseOptionViewSet,
    basename="program-phase-options",
)

# Map the router-generated URLs to the application's root path.
urlpatterns = [path("", include(router.urls))]
