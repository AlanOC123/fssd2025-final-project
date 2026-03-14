import pytest
from rest_framework.test import APIClient

pytestmark = pytest.mark.django_db


@pytest.fixture
def get_response():
    def make_request(url_name):
        client = APIClient()
        return client.get(f"/api/v1/biology/{url_name}/")

    return make_request
