from django.urls import include, path
from rest_framework.routers import DefaultRouter

from .views import MuscleGroupViewSet, MuscleViewSet

router = DefaultRouter()

router.register(prefix="muscles", viewset=MuscleViewSet, basename="muscles")
router.register(
    prefix="muscle-groups", viewset=MuscleGroupViewSet, basename="muscle-groups"
)

urlpatterns = [path("", include(router.urls))]
