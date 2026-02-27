from django.urls import include, path
from rest_framework.routers import DefaultRouter

from .views import (
    EquipmentViewset,
    ExerciseMovementViewset,
    ExercisePhaseViewset,
    ExerciseViewset,
    JointContributionViewset,
    JointRangeOfMotionViewset,
)

router = DefaultRouter()

router_struct = [
    {"prefix": r"equipment", "viewset": EquipmentViewset, "basename": "equipment"},
    {
        "prefix": r"exercise-list",
        "viewset": ExerciseViewset,
        "basename": "exercise_list",
    },
    {
        "prefix": r"exercise-movements",
        "viewset": ExerciseMovementViewset,
        "basename": "exercise_movements",
    },
    {
        "prefix": r"exercise-phases",
        "viewset": ExercisePhaseViewset,
        "basename": "exercise_phases",
    },
    {
        "prefix": r"joint-contributions",
        "viewset": JointContributionViewset,
        "basename": "joint_contributions",
    },
    {
        "prefix": r"joint-ranges-of-motion",
        "viewset": JointRangeOfMotionViewset,
        "basename": "joint_ranges_of_motion",
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

print("Exercise urls registered...")

urlpatterns = [path("", include(router.urls))]
