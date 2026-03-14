from django.contrib import admin
from django.urls import include, path

api_base = "api/v1"

urlpatterns = [
    path("admin/", admin.site.urls),
    # Auth Endpoints
    path(f"{api_base}/auth/", include("dj_rest_auth.urls")),
    path(f"{api_base}/auth/registration/", include("dj_rest_auth.registration.urls")),
    # App Endpoints
    path(f"{api_base}/users/", include("apps.users.urls")),
    path(f"{api_base}/programs/", include("apps.programs.urls")),
    path(f"{api_base}/biology/", include("apps.biology.urls")),
    path(f"{api_base}/exercises/", include("apps.exercises.urls")),
]
