import pytest
from django.db import connection
from django.urls import reverse

from secure_notes.models import Note

NOTES_URL = "/api/notes/"


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
def test_markdown_sanitises_unsafe_links_and_removes_images(client, user):
    client.login(username="testuser", password="testpass")

    note = Note.objects.create(
        owner=user,
        title="Unsafe Markdown Link",
        content="""
[Click me](javascript:alert('xss'))

<img
    src="https://example.com/image.png"
    onerror="alert('xss')"
    onload="alert('xss)">

<a href="javascript:alert('XSS')">
    Raw link</a>
""",
    )

    response = client.get(reverse("secure_notes:note_detail", args=[note.id]))

    assert response.status_code == 200

    content = response.content.decode()

    assert "javascript:alert" not in content
    assert "onerror" not in content
    assert "onload" not in content
    assert "<img" not in content
    assert "example.com/image.png" not in content


    assert "Click me" in content
    assert "Raw link" in content
