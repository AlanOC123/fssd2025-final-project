from django.urls import include, path
from rest_framework.routers import DefaultRouter

from .views import (
    EquipmentViewSet,
    ExerciseViewSet,
)

router = DefaultRouter()

router.register(prefix=r"exercises", viewset=ExerciseViewSet, basename="exercises")
router.register(prefix=r"equipment", viewset=EquipmentViewSet, basename="equipment")

urlpatterns = [path("", include(router.urls))]
