import pytest
from rest_framework.test import APIClient
from django.contrib.auth import get_user_model

User = get_user_model()

@pytest.mark.django_db
def test_authentication_required_for_notes_api():
    client = APIClient()
    response = client.get('/api/notes/')
    assert response.status_code in (403, 401)  # Should be forbidden for unauthenticated users

@pytest.mark.django_db
def test_authentication_for_logged_in_user():
    User.objects.create_user(username='testuser', password='testpass')
    client = APIClient()
    assert client.login(username='testuser', password='testpass')
    
    response = client.get('/api/notes/')
    assert response.status_code == 200  # Should be accessible for authenticated users
    assert response.data == []  # Should return an empty list for a new user with no notes

@pytest.mark.django_db
def test_create_note_api():
    # Create a test user
    User.objects.create_user(username='testuser', password='testpass')
    
    # Authenticate the API client
    client = APIClient()
    assert client.login(username='testuser', password='testpass')
    
    # Create a note via the API
    response = client.post('/api/notes/', {'title': 'Test Note', 'content': 'This is a test note.'}, format='json')
    assert response.status_code == 201  # Should be created successfully
    assert response.data['title'] == 'Test Note'
    assert response.data['content'] == 'This is a test note.'
    
    
@pytest.mark.django_db
def test_user_cannot_access_others_notes():
    # Create two users
    User.objects.create_user(username='user_a', password='pass1')
    User.objects.create_user(username='user_b', password='pass2')
    
    # Create a note for user_a
    client_a = APIClient()
    assert client_a.login(username='user_a', password='pass1')
    response =client_a.post('/api/notes/', {'title': 'User A Note', 'content': 'This is a note for user A.'}, format='json')
    assert response.status_code == 201
    note_id = response.data['id']# Get the ID of the created note
    
    client_b = APIClient()
    assert client_b.login(username='user_b', password='pass2')
    
    response = client_b.get('/api/notes/')
    assert response.status_code == 200
    assert len(response.data) == 0  # User_b should not see user_a's note
    
    # Attempt to access notes (should be empty for user_b)
    response = client_b.get(f'/api/notes/{note_id}/')
    assert response.status_code == 404  # Should return 404 for non-existent note for user_b.
    
@pytest.mark.django_db
def test_duplicate_title_for_same_user():
    # Create a test user and a note with a specific title - api response.
    User.objects.create_user(username='testuser', password='testpass')
    
    # Attempt to create another note with the same title for the same user - api response.
    client = APIClient()
    assert client.login(username='testuser', password='testpass')
    response = client.post('/api/notes/', {'title': 'Duplicate Title', 'content': 'First note content.'},format='json')
    assert response.status_code == 201  # First note should be created successfully
    
    response = client.post('/api/notes/', {'title': 'Duplicate Title', 'content': 'Second note content.'}, format='json')
    assert response.status_code == 400  # Should return a bad request due to unique constraint
    assert 'title' in response.data  # Should indicate the error is with the title field