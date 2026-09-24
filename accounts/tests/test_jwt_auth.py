import pytest
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient

NOTES_URL = "/api/notes/"


# Tests to ensure that invalid tokens cannot access the notes API.
@pytest.mark.django_db
def test_invalid_token_cannot_access_notes():
    client = APIClient()
    client.credentials(HTTP_AUTHORIZATION="Bearer invalidtoken")
    response = client.get(NOTES_URL)
    assert response.status_code in (403, 401)


@pytest.mark.django_db
def test_token_refresh_endpoint_is_throttled():
    client = APIClient()
    url = reverse("token_refresh")
    payload = {"refresh": "invalid-token"}

    responses = [
        client.post(url, payload, format="json")
        for _ in range(6)
    ]

    for response in responses[:5]:
        assert response.status_code in (
            status.HTTP_400_BAD_REQUEST,
            status.HTTP_401_UNAUTHORIZED,
        )

    assert responses[5].status_code == status.HTTP_429_TOO_MANY_REQUESTS


@pytest.mark.django_db
def test_token_endpoint_is_throttled():
    client = APIClient()
    url = reverse("token_obtain_pair")

    payload = {
        "username": "wrong-user",
        "password": "wrong-password",
    }

    responses = [
        client.post(url, payload, format="json")
        for _ in range(6)
    ]

    for response in responses[:5]:
        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    assert responses[5].status_code == status.HTTP_429_TOO_MANY_REQUESTS
