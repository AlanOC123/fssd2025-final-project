from django.urls import include, path
from rest_framework.routers import DefaultRouter

from .views import (
    ExperienceLevelViewset,
    TrainerClientMembershipViewset,
    TrainerMatchingViewset,
    TrainingGoalViewset,
)

router = DefaultRouter()

router.register(
    prefix="experience-levels",
    viewset=ExperienceLevelViewset,
    basename="experience-levels",
)
router.register(
    prefix="trainer-client-memberships",
    viewset=TrainerClientMembershipViewset,
    basename="trainer-client-memberships",
)
router.register(
    prefix="training-goals",
    viewset=TrainingGoalViewset,
    basename="training-goals",
)
router.register(
    prefix="find-trainers",
    viewset=TrainerMatchingViewset,
    basename="find-trainers",
)

urlpatterns = [path("", include(router.urls))]
