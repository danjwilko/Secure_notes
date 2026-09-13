from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated

from .models import Note
from .serializers import NoteSerializer


class NoteViewSet(viewsets.ModelViewSet):
    """ViewSet for the Note model,
    providing CRUD operations for authenticated users."""

    queryset = Note.objects.none()
    serializer_class = NoteSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        """Return notes belonging to the authenticated user only."""
        return Note.objects.filter(owner=self.request.user)

    def perform_create(self, serializer):
        """Set the owner of the note to the current authenticated user."""
        serializer.save(owner=self.request.user)
