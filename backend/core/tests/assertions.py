from rest_framework import status


def assert_public_reference_endpoint(api_client, url, expected_count):
    response = api_client.get(url)

    data = response.data
    items = data["results"] if isinstance(data, dict) else data

    assert response.status_code == status.HTTP_200_OK
    assert len(items) == expected_count
