from django.urls import include, path
from rest_framework.routers import DefaultRouter

from apps.programs.views import (
    ProgramPhaseOptionViewSet,
    ProgramPhaseViewSet,
    ProgramViewSet,
)

router = DefaultRouter()
router.register(r"programs", ProgramViewSet, basename="programs")
router.register(r"program-phases", ProgramPhaseViewSet, basename="program-phases")
router.register(
    r"program-phase-options",
    ProgramPhaseOptionViewSet,
    basename="program-phase-options",
)

urlpatterns = [path("", include(router.urls))]
