"""Defines URL patterns for the secure_notes app."""

from django.urls import path

from . import views

app_name = 'secure_notes'
urlpatterns = [
    # Home page showing list of notes.
    path('', views.index, name='index'),
    # List of notes for the logged-in user.
    path('notes/', views.notes, name='notes'),
    # Additional URL patterns for note detail, create, update, delete.
    # Detail page for a specific note.
    path('notes/<int:note_id>/', views.note_detail, name='note_detail'),
    # Create a new note.
    path('notes/create/', views.create_note, name='create_note'),
    # Update an existing note.
    path('edit_note/<int:note_id>/', views.edit_note, name='edit_note'),
    # Delete a note.
    path('delete_note/<int:note_id>/', views.delete_note, name='delete_note'),
    ]