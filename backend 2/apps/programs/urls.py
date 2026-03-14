from django.urls import include, path
from rest_framework.routers import DefaultRouter

from apps.programs.views import (
    ProgramPhaseOptionViewset,
    ProgramPhaseViewset,
    ProgramViewSet,
)

router = DefaultRouter()

router_struct = [
    {"prefix": r"program-list", "viewset": ProgramViewSet, "basename": "program_list"},
    {
        "prefix": r"program-phases",
        "viewset": ProgramPhaseViewset,
        "basename": "program_phases",
    },
    {
        "prefix": r"program-phase-options",
        "viewset": ProgramPhaseOptionViewset,
        "basename": "program_phase_options",
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

print("Program urls registered...")

urlpatterns = [path("", include(router.urls))]
