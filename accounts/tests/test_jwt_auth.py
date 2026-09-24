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
def test_token_refresh_endpoint_is_throttled(settings):
    settings.REST_FRAMEWORK["DEFAULT_THROTTLE_RATES"]["login"] = "2/minute"

    client = APIClient()
    url = reverse("token_refresh")

    payload = {"refresh": "invalid-token"}

    response_1 = client.post(url, payload, format="json")
    response_2 = client.post(url, payload, format="json")
    response_3 = client.post(url, payload, format="json")

    assert response_1.status_code in [
        status.HTTP_401_UNAUTHORIZED,
        status.HTTP_400_BAD_REQUEST,
    ]

    assert response_2.status_code in [
        status.HTTP_401_UNAUTHORIZED,
        status.HTTP_400_BAD_REQUEST,
    ]
    assert response_3.status_code == status.HTTP_429_TOO_MANY_REQUESTS


@pytest.mark.django_db
def test_token_endpoint_is_throttled(settings):
    settings.REST_FRAMEWORK["DEFAULT_THROTTLE_RATES"]["login"] = "2/minute"

    client = APIClient()
    url = reverse("token_obtain_pair")

    payload = {
        "username": "wrong-user",
        "password": "wrong-password",
    }

    response_1 = client.post(url, payload, format="json")
    response_2 = client.post(url, payload, format="json")
    response_3 = client.post(url, payload, format="json")

    assert response_1.status_code == status.HTTP_401_UNAUTHORIZED
    assert response_2.status_code == status.HTTP_401_UNAUTHORIZED
    assert response_3.status_code == status.HTTP_429_TOO_MANY_REQUESTS
