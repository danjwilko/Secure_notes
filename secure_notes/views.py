from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required

from .models import Note
from .forms import NoteForm

def index(request):
    """View function for the home page of the secure notes app."""
    return render(request, 'secure_notes/index.html')

@login_required
def notes(request):
    """View function to display the list of notes for the logged-in user."""
    # Fetch notes for the current user, ordered by last updated time descending.
    notes = Note.objects.filter(owner=request.user).order_by('-updated_at')
    context = {
        'notes': notes
    }
    
    return render(request, 'secure_notes/notes.html', context)

@login_required
def note_detail(request, note_id):
    """View function to display the details of a specific note."""
    # Fetch the note by ID and ensure it belongs to the current user.
    note = Note.objects.get(id=note_id, owner=request.user)
    context = {
        'note': note
    }
    
    return render(request, 'secure_notes/note_detail.html', context)

@login_required
def create_note(request):
    """View function to handle the creation of a new note."""
    if request.method != 'POST':
        form = NoteForm()
    else:
        # Process the submitted form data.
        form = NoteForm(data=request.POST)
        if form.is_valid():
            # Create a new note instance but don't save to the database yet.
            new_note = form.save(commit=False)
            # Assign the current user as the owner of the note.
            new_note.owner = request.user
            # Save the note to the database.
            new_note.save()
            return redirect('secure_notes:notes')
    # Display a blank form for creating a new note.
    context = {
        'form': form
    }
    return render(request, 'secure_notes/create_note.html', context)

@login_required
def edit_note(request, note_id):
    """View function to handle editing an existing note."""
    # Fetch the note by ID and ensure it belongs to the current user.
    note = Note.objects.get(id=note_id, owner=request.user)
    
    if request.method != 'POST':
        # Pre-fill the form with the existing note data.
        form = NoteForm(instance=note)
    else:
        # Process the submitted form data.
        form = NoteForm(instance=note, data=request.POST)
        if form.is_valid():
            form.save()
            return redirect('secure_notes:notes')
    
    context = {
        'form': form,
        'note': note
    }
    
    return render(request, 'secure_notes/edit_note.html', context)