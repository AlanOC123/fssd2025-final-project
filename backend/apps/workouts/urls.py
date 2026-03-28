"""URL routing configuration for the workouts application.

This module defines the API endpoints for managing workout prescriptions,
exercises, sets, and their respective completion records using the
Django REST Framework DefaultRouter.
"""

from django.urls import include, path
from rest_framework.routers import DefaultRouter

from apps.workouts.views import (
    WorkoutExerciseRecordViewSet,
    WorkoutExerciseViewSet,
    WorkoutSessionViewSet,
    WorkoutSetRecordViewSet,
    WorkoutSetViewSet,
    WorkoutViewSet,
)

# Initialize the REST router and register viewsets for the workouts API.
router = DefaultRouter()

router.register(r"workouts", WorkoutViewSet, basename="workouts")
router.register(
    r"workout-exercises", WorkoutExerciseViewSet, basename="workout-exercises"
)
router.register(r"workout-sets", WorkoutSetViewSet, basename="workout-sets")
router.register(r"workout-sessions", WorkoutSessionViewSet, basename="workout-sessions")
router.register(
    r"exercise-records", WorkoutExerciseRecordViewSet, basename="exercise-records"
)
router.register(r"set-records", WorkoutSetRecordViewSet, basename="set-records")

urlpatterns = [path("", include(router.urls))]
