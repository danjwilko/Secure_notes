import re

import pytest
from django.contrib.auth import get_user_model
from django.db import connection
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient
from rest_framework.throttling import SimpleRateThrottle
from rest_framework_simplejwt.tokens import RefreshToken

from secure_notes.models import Note

User = get_user_model()
NOTES_URL = "/api/notes/"


@pytest.fixture(autouse=True)
def clear_throttle_cache():
    SimpleRateThrottle.cache.clear()


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


# Tests to ensure that invalid tokens cannot access the notes API.
@pytest.mark.django_db
def test_invalid_token_cannot_access_notes():
    client = APIClient()
    client.credentials(HTTP_AUTHORIZATION="Bearer invalidtoken")
    response = client.get(NOTES_URL)
    assert response.status_code in (403, 401)


# Basic tests to ensure authentication is required and
# that authenticated users can access the notes API.
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


# Tests for creating, updating, and deleting notes.
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
def test_note_partial_update(user, api_client):
    client = api_client(user)
    response = client.post(
        NOTES_URL,
        {"title": "Original Title", "content": "Original content."},
        format="json",
    )

    assert response.status_code == 201
    note_id = response.data["id"]

    response = client.patch(
        f"{NOTES_URL}{note_id}/",
        {"content": "Partially updated content."},
        format="json",
    )

    assert response.status_code == 200
    assert response.data["title"] == "Original Title"
    assert response.data["content"] == "Partially updated content."


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


# Tests for validation errors when creating or updating notes.
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


# Tests to ensure duplicate titles are not allowed for the same user,
# but different users can have notes with the same title.
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
        NOTES_URL,
        {"title": "Duplicate Title", "content": "Second note content."},
        format="json",
    )

    assert response.status_code == 400
    assert "title" in response.data


@pytest.mark.django_db
def test_same_title_different_users(user, api_client):
    client_a = api_client(user)

    response = client_a.post(
        NOTES_URL,
        {"title": "Shared Title", "content": "User A's note content."},
        format="json",
    )

    assert response.status_code == 201

    user_b = User.objects.create_user(
        username="testuser2", password="testpass2"
    )
    client_b = api_client(user_b)

    response = client_b.post(
        NOTES_URL,
        {"title": "Shared Title", "content": "User B's note content."},
        format="json",
    )

    assert response.status_code == 201


# Tests to ensure users cannot access, update, or delete others' notes.
@pytest.mark.django_db
def test_notes_list_only_shows_current_users_notes(user, api_client):
    client_a = api_client(user)

    response = client_a.post(
        NOTES_URL,
        {"title": "User A Note", "content": "This is a note for user A."},
        format="json",
    )

    assert response.status_code == 201

    user_b = User.objects.create_user(
        username="testuser2", password="testpass2"
    )
    client_b = api_client(user_b)

    response = client_b.post(
        NOTES_URL,
        {"title": "User B Note", "content": "This is a note for user B."},
        format="json",
    )

    assert response.status_code == 201

    response = client_a.get(NOTES_URL)
    assert response.status_code == 200
    assert response.data["count"] == 1
    assert response.data["results"][0]["title"] == "User A Note"
    assert response.data["results"][0]["title"] != "User B Note"


@pytest.mark.django_db
def test_user_cannot_retrieve_another_users_note(user, api_client):
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

    response = client_b.get(f"{NOTES_URL}{note_id}/")
    assert (
        response.status_code == 404
    )  # Hidden because it is outside of user_b's queryset.


@pytest.mark.django_db
def test_user_cannot_update_another_users_note(user, api_client):
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

    assert response.status_code == 404


@pytest.mark.django_db
def test_user_cannot_delete_another_users_note(user, api_client):
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

    response = client_b.delete(f"{NOTES_URL}{note_id}/")
    assert response.status_code == 404


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


@pytest.mark.django_db
def test_token_refresh_endpoint_is_throttled(user, api_client, settings):
    settings.REST_FRAMEWORK["DEFAULT_THROTTLE_RATES"]["login"] = "2/minute"

    client = api_client(user)
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
def test_notes_api_is_throttled_for_authenticated_users(
    user, api_client, settings
):
    settings.REST_FRAMEWORK["DEFAULT_THROTTLE_RATES"]["user"] = "2/minute"

    client = api_client(user)

    response_1 = client.get(NOTES_URL)
    response_2 = client.get(NOTES_URL)
    response_3 = client.get(NOTES_URL)

    assert response_1.status_code == 200
    assert response_2.status_code == 200
    assert response_3.status_code == 429


@pytest.mark.django_db
def test_note_content_is_encrypted_at_rest(user, api_client):
    client = api_client(user)

    response = client.post(
        NOTES_URL,
        {
            "title": "Encryption Test",
            "content": "This content should be encrypted.",
        },
        format="json",
    )

    assert response.status_code == 201
    assert response.data["content"] == "This content should be encrypted."

    note = Note.objects.get(id=response.data["id"])

    assert note.content == "This content should be encrypted."
    with connection.cursor() as cursor:
        cursor.execute(
            "SELECT content FROM secure_notes_note WHERE id = %s", [note.id]
        )
        raw_content = cursor.fetchone()[0]

    assert raw_content != "This content should be encrypted."
    assert "This content should be encrypted." not in raw_content


@pytest.mark.django_db
def test_malformed_note_request_returns_400(user, api_client):
    client = api_client(user)

    response = client.post(
        NOTES_URL,
        {"title": [], "content": {}},
        format="json",
    )

    assert response.status_code == 400


@pytest.mark.django_db
def test_large_note_content(user, api_client):
    client = api_client(user)

    large_content = "A" * 10000

    response = client.post(
        NOTES_URL,
        {"title": "Large Note", "content": large_content},
        format="json",
    )

    assert response.status_code == 201
    assert response.data["content"] == large_content


@pytest.mark.django_db
def test_note_detail_sanitises_markdown_output(client, user):
    client.login(username="testuser", password="testpass")

    note = Note.objects.create(
        owner=user,
        title="Unsafe Markdown",
        content='<script>alert("xss")</script>**Safe text**',
    )

    response = client.get(reverse("secure_notes:note_detail", args=[note.id]))

    assert response.status_code == 200

    content = response.content.decode()

    assert '<script>alert("xss")</script>' not in content
    assert 'alert("xss")' in content
    assert "<strong>Safe text</strong>" in content


@pytest.mark.django_db
def test_markdown_sanitises_unsafe_links_and_image_attributes(client, user):
    client.login(username="testuser", password="testpass")

    note = Note.objects.create(
        owner=user,
        title="Unsafe Markdown Link",
        content="""
[Click me](javascript:alert('xss'))

![Bad image]("onerror="alert('xss'))

<a href="javascript:alert('XSS')">Raw link</a>
""",
    )

    response = client.get(reverse("secure_notes:note_detail", args=[note.id]))

    assert response.status_code == 200

    content = response.content.decode()

    assert "javascript:alert" not in content
    assert "onerror" not in content
    assert "onload" not in content
    assert "Click me" in content
    assert "Raw link" in content


# Tests for password change and reset - (not for API endpoints)
@pytest.mark.django_db
def test_user_can_change_password(client, user):
    client.login(username="testuser", password="testpass")

    response = client.post(
        reverse("accounts:password_change"),
        {
            "old_password": "testpass",
            "new_password1": "newstrongpassword123",
            "new_password2": "newstrongpassword123",
        },
    )

    assert response.status_code == 302
    user.refresh_from_db()
    assert user.check_password("newstrongpassword123")


@pytest.mark.django_db
def test_user_can_reset_password(client, user, mailoutbox):
    user.email = "test@test.com"
    user.save()

    # Here we request the reset email.
    response = client.post(
        reverse("accounts:password_reset"),
        {"email": "test@test.com"},
    )

    assert response.status_code == 302
    assert len(mailoutbox) == 1

    email = mailoutbox[0].body
    url_match = re.search(
        r'(/accounts/password_reset_confirm/[^">\s]+)', email
    )
    url = url_match.group(1)

    response = client.get(url, follow=True)

    assert response.status_code == 200
    post_url = response.redirect_chain[-1][0]

    response = client.post(
        post_url,
        {
            "new_password1": "newstrongpassword123",
            "new_password2": "newstrongpassword123",
        },
        follow=True,
    )
    assert response.status_code == 200

    user.refresh_from_db()
    assert user.check_password("newstrongpassword123")
