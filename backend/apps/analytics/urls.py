"""URL configuration for the analytics application.

This module defines the API endpoints for exercise-specific analytics, including
historical load tracking and predictive next-session recommendations.
"""

from django.urls import path

from .views import ExerciseLoadHistoryView, NextSessionRecommendationView

urlpatterns = [
    # Endpoint to retrieve the historical progression of load and 1RM for an exercise
    path(
        "programs/<uuid:program_id>/exercises/<uuid:exercise_id>/load-history/",
        ExerciseLoadHistoryView.as_view(),
        name="exercise-load-history",
    ),
    # Endpoint to retrieve recommended load and weight bands for the next session
    path(
        "programs/<uuid:program_id>/exercises/<uuid:exercise_id>/next-session/",
        NextSessionRecommendationView.as_view(),
        name="next-session-recommendation",
    ),
]
