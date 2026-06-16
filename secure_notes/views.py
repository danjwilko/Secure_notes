import logging

from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404, redirect, render

from .forms import NoteForm
from .models import Note
from .utils import render_markdown

logger = logging.getLogger(__name__)


def user_notes_qs(request):
    """Helper function to get the queryset of notes belonging to the logged-in
    user."""
    return Note.objects.filter(owner=request.user)


def get_user_note_or_404(request, note_id):
    """Helper function to get a note by ID and ensure it belongs to the
    user."""
    return get_object_or_404(user_notes_qs(request), id=note_id)


def index(request):
    """View function for the home page of the secure notes app."""
    if request.user.is_authenticated:
        return redirect("secure_notes:notes")
    return render(request, "secure_notes/index.html")


@login_required
def dashboard(request):
    notes = Note.objects.filter(owner=request.user)

    context = {
        "note_count": notes.count(),
        "latest_note": notes.order_by("-created_at").first(),
        "recently_updated": notes.order_by("-updated_at").first(),
        "recent_notes": notes.order_by("-updated_at")[:4],
    }

    return render(request, "secure_notes/dashboard.html", context)


@login_required
def notes(request):
    """View function to display the list of notes for the logged-in user."""
    # Fetch notes for the current user, ordered by last updated time.
    notes = user_notes_qs(request).order_by("-updated_at")
    context = {"notes": notes}
    return render(request, "secure_notes/notes.html", context)


@login_required
def note_detail(request, note_id):
    """View function to display the details of a specific note."""
    # Fetch the note by ID and ensure it belongs to the current user.
    note = get_user_note_or_404(request, note_id)
    context = {
        "note": note,
        "rendered_content": render_markdown(note.content),
    }

    return render(request, "secure_notes/note_detail.html", context)


@login_required
def create_note(request):
    """View function to handle the creation of a new note."""
    if request.method != "POST":
        form = NoteForm(user=request.user)
    else:
        # Process the submitted form data, check for title uniqueness.
        form = NoteForm(request.POST or None, user=request.user)
        if form.is_valid():
            # Create a new note instance but don't save to the database yet.
            new_note = form.save(commit=False)
            # Assign the current user as the owner of the note.
            new_note.owner = request.user
            # Save the note to the database.
            new_note.save()
            logger.info(
                "Note created user=%s note_id=%s",
                request.user.username,
                new_note.id,
            )
            return redirect("secure_notes:notes")
    # Display a blank form for creating a new note.
    context = {"form": form}
    return render(request, "secure_notes/create_note.html", context)


@login_required
def edit_note(request, note_id):
    """View function to handle editing an existing note."""
    # Fetch the note by ID and ensure it belongs to the current user.
    note = get_user_note_or_404(request, note_id)

    if request.method != "POST":
        # Pre-fill the form with the existing note data.
        form = NoteForm(instance=note, user=request.user)
    else:
        # Process the submitted form data.
        form = NoteForm(instance=note, data=request.POST, user=request.user)
        if form.is_valid():
            form.save()
            logger.info()(
                "Note edited user=%s note_id=%s",
                request.user.username,
                note.id,
            )
            return redirect("secure_notes:note_detail", note_id=note.id)

    context = {"form": form, "note": note}

    return render(request, "secure_notes/edit_note.html", context)


@login_required
def delete_note(request, note_id):
    """View function to handle deleting a note."""
    # Fetch the note by ID and ensure it belongs to the current user.
    note = get_user_note_or_404(request, note_id)

    if request.method == "POST":
        note.delete()
        logger.warning()(
            "Note deleted user=%s note_id=%s", request.user.username, note.id
        )
        return redirect("secure_notes:notes")

    context = {"note": note}

    return render(request, "secure_notes/delete_note.html", context)
