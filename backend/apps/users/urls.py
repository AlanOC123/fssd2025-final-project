from django.urls import include, path
from rest_framework.routers import DefaultRouter

from .views import (
    ExperienceLevelViewset,
    MembershipStatusViewset,
    TrainerClientMembershipViewset,
    TrainingGoalViewset,
)

router = DefaultRouter()

router_struct = [
    {
        "prefix": r"experience-levels",
        "viewset": ExperienceLevelViewset,
        "basename": "experience_levels",
    },
    {
        "prefix": r"membership-status",
        "viewset": MembershipStatusViewset,
        "basename": "membership_status",
    },
    {
        "prefix": r"trainer-client-memberships",
        "viewset": TrainerClientMembershipViewset,
        "basename": "trainer_client_memberships",
    },
    {
        "prefix": r"training-goals",
        "viewset": TrainingGoalViewset,
        "basename": "training_goals",
    },
]

for route in router_struct:
    prefix = route["prefix"]
    viewset = route["viewset"]
    basename = route["basename"]

    print(f"Registering route: {prefix}")

    try:
        router.register(prefix=prefix, viewset=viewset, basename=basename)
    except Exception as e:
        print(f"Error registering route: {e}")

print("User urls registered...")

urlpatterns = [path("", include(router.urls))]
