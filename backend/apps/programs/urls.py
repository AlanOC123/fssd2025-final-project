from django.urls import include, path
from rest_framework.routers import DefaultRouter

from apps.programs.views import ProgramPhaseViewSet, ProgramViewSet

router = DefaultRouter()
router.register(r"programs", ProgramViewSet, basename="programs")
router.register(r"program-phases", ProgramPhaseViewSet, basename="program-phases")

urlpatterns = [path("", include(router.urls))]
