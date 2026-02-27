from django.urls import include, path
from rest_framework.routers import DefaultRouter

from .views import (
    AnatomicalDirectionViewset,
    JointActionViewset,
    JointViewset,
    MovementPatternViewset,
    MuscleInvolvementViewset,
    MuscleRoleViewset,
    MuscleViewset,
    PlaneOfMotionViewset,
)

router = DefaultRouter()

router_struct = [
    {
        "prefix": r"muscle-involvement",
        "viewset": MuscleInvolvementViewset,
        "basename": "muscle_involvement",
    },
    {
        "prefix": r"anatomical-direction",
        "viewset": AnatomicalDirectionViewset,
        "basename": "anatomical_direction",
    },
    {
        "prefix": r"joint-action",
        "viewset": JointActionViewset,
        "basename": "joint_action",
    },
    {
        "prefix": r"joint",
        "viewset": JointViewset,
        "basename": "joint",
    },
    {
        "prefix": r"movement-pattern",
        "viewset": MovementPatternViewset,
        "basename": "movement_pattern",
    },
    {
        "prefix": r"muscle-role",
        "viewset": MuscleRoleViewset,
        "basename": "muscle_role",
    },
    {"prefix": r"muscle", "viewset": MuscleViewset, "basename": "muscle"},
    {
        "prefix": r"plane-of-motion",
        "viewset": PlaneOfMotionViewset,
        "basename": "plane_of_motion",
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

print("Biology urls registered...")

urlpatterns = [path("", include(router.urls))]
