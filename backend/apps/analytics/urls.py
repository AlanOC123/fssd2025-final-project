from django.urls import path

from .views import ExerciseLoadHistoryView, NextSessionRecommendationView

urlpatterns = [
    path(
        "programs/<uuid:program_id>/exercises/<uuid:exercise_id>/load-history/",
        ExerciseLoadHistoryView.as_view(),
        name="exercise-load-history",
    ),
    path(
        "programs/<uuid:program_id>/exercises/<uuid:exercise_id>/next-session/",
        NextSessionRecommendationView.as_view(),
        name="next-session-recommendation",
    ),
]
