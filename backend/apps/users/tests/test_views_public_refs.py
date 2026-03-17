import pytest
from django.contrib.auth import get_user_model
from model_bakery import baker
from rest_framework import status
from rest_framework.test import APIClient

from apps.users.models import (
    ExperienceLevel,
    TrainingGoal,
)

User = get_user_model()
pytestmark = pytest.mark.django_db


@pytest.fixture
def public_reference_world():
    baker.make(TrainingGoal, _quantity=3)
    baker.make(ExperienceLevel, _quantity=3)


@pytest.mark.parametrize("url_name", ["training-goals", "experience-levels"])
def test_public_endpoints(public_reference_world, url_name):
    response = APIClient().get(f"/api/v1/users/{url_name}/")
    data = response.data["results"] if "results" in response.data else response.data
    assert response.status_code == status.HTTP_200_OK
    assert len(data) >= 3
