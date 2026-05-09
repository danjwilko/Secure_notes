from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated

from .models import Note
from .serializers import NoteSerializer


class NoteViewSet(viewsets.ModelViewSet):
    """ViewSet for the Note model."""

    queryset = Note.objects.all()  # This will be overridden by get_queryset
    serializer_class = NoteSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        """Return notes for the current authenticated user only."""
        return Note.objects.filter(owner=self.request.user)

    def perform_create(self, serializer):
        """Set the owner of the note to the current authenticated user."""
        serializer.save(owner=self.request.user)
