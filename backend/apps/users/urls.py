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

router = DefaultRouter()

router.register(
    prefix="experience-levels",
    viewset=ExperienceLevelViewSet,
    basename="experience-levels",
)
router.register(
    prefix="trainer-client-memberships",
    viewset=TrainerClientMembershipViewSet,
    basename="trainer-client-memberships",
)
router.register(
    prefix="training-goals",
    viewset=TrainingGoalViewSet,
    basename="training-goals",
)
router.register(
    prefix="find-trainers",
    viewset=TrainerMatchingViewSet,
    basename="find-trainers",
)

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

urlpatterns = [path("", include(router.urls))]
