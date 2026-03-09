import pytest
from django.contrib.auth import get_user_model
from rest_framework.test import APIClient
from rest_framework_simplejwt.tokens import RefreshToken

User = get_user_model()
NOTES_URL = "/api/notes/"


def get_token_for_user(user):
    """Helper function to obtain JWT token for a user."""
    refresh = RefreshToken.for_user(user)
    return {"refresh": str(refresh), "access": str(refresh.access_token)}


@pytest.fixture
def user():
    """Fixture to create a test user."""
    return User.objects.create_user(username="testuser", password="testpass")


@pytest.fixture
def api_client():
    def make_client(user):
        client = APIClient()
        token = get_token_for_user(user)
        client.credentials(HTTP_AUTHORIZATION=f"Bearer {token['access']}")
        return client

    return make_client


@pytest.mark.django_db
def test_authentication_required_for_notes_api():
    client = APIClient()
    response = client.get(NOTES_URL)
    assert response.status_code in (403, 401)


@pytest.mark.django_db
def test_authenticated_user_can_access_notes(user, api_client):
    client = api_client(user)

    response = client.get(NOTES_URL)

    assert response.status_code == 200
    assert response.data["count"] == 0
    assert response.data["results"] == []


@pytest.mark.django_db
def test_create_note_api(user, api_client):
    client = api_client(user)

    response = client.post(
        NOTES_URL,
        {"title": "Test Note", "content": "This is a test note."},
        format="json",
    )

    assert response.status_code == 201
    assert response.data["title"] == "Test Note"
    assert response.data["content"] == "This is a test note."


@pytest.mark.django_db
def test_user_cannot_access_others_notes(user, api_client):
    client_a = api_client(user)

    response = client_a.post(
        NOTES_URL,
        {"title": "User A Note", "content": "This is a note for user A."},
        format="json",
    )

    assert response.status_code == 201
    note_id = response.data["id"]

    user_b = User.objects.create_user(
        username="testuser2", password="testpass2"
    )
    client_b = api_client(user_b)

    response = client_b.get(NOTES_URL)

    assert response.status_code == 200
    assert response.data["count"] == 0
    assert response.data["results"] == []

    response = client_b.get(f"{NOTES_URL}{note_id}/")
    assert (
        response.status_code == 404
    )  # Should return 404 for non-existent note for user_b.


@pytest.mark.django_db
def test_duplicate_title_for_same_user(user, api_client):
    client = api_client(user)

    response = client.post(
        NOTES_URL,
        {"title": "Duplicate Title", "content": "First note content."},
        format="json",
    )

    assert response.status_code == 201

    response = client.post(
        "/api/notes/",
        {"title": "Duplicate Title", "content": "Second note content."},
        format="json",
    )

    assert response.status_code == 400
    assert "title" in response.data


@pytest.mark.django_db
def test_note_update(user, api_client):
    client = api_client(user)
    response = client.post(
        NOTES_URL,
        {"title": "Original Title", "content": "Original content."},
        format="json",
    )

    assert response.status_code == 201
    note_id = response.data["id"]

    response = client.put(
        f"{NOTES_URL}{note_id}/",
        {"title": "Updated Title", "content": "Updated content."},
        format="json",
    )

    assert response.status_code == 200
    assert response.data["title"] == "Updated Title"
    assert response.data["content"] == "Updated content."


@pytest.mark.django_db
def test_user_cannot_update_others_note(user, api_client):
    client_a = api_client(user)
    response = client_a.post(
        NOTES_URL,
        {"title": "User A Note", "content": "This is a note for user A."},
        format="json",
    )

    assert response.status_code == 201
    note_id = response.data["id"]

    user_b = User.objects.create_user(
        username="testuser2", password="testpass2"
    )
    client_b = api_client(user_b)

    response = client_b.put(
        f"{NOTES_URL}{note_id}/",
        {"title": "Hacked Title", "content": "Hacked content."},
        format="json",
    )

    assert response.status_code in (404, 403)


@pytest.mark.django_db
def test_note_deletion(user, api_client):
    client = api_client(user)

    response = client.post(
        NOTES_URL,
        {"title": "Note to Delete", "content": "This note will be deleted."},
        format="json",
    )

    assert response.status_code == 201
    note_id = response.data["id"]

    response = client.delete(f"{NOTES_URL}{note_id}/")
    assert response.status_code == 204

    response = client.get(f"{NOTES_URL}{note_id}/")
    assert response.status_code == 404


@pytest.mark.django_db
def test_note_requires_title(user, api_client):
    client = api_client(user)

    response = client.post(
        NOTES_URL, {"content": "Missing title"}, format="json"
    )

    assert response.status_code == 400
    assert "title" in response.data


@pytest.mark.django_db
def test_note_requires_content(user, api_client):
    client = api_client(user)

    response = client.post(
        NOTES_URL, {"title": "Missing content"}, format="json"
    )

    assert response.status_code == 400
    assert "content" in response.data
