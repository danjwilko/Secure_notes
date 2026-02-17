from rest_framework import viewsets, permissions
from .serializers import NoteSerializer
from .models import Note
    
class NoteViewSet(viewsets.ModelViewSet):
    """ViewSet for the Note model."""
        
    serializer_class = NoteSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        """Return notes for the current authenticated user only."""
        return Note.objects.filter(owner=self.request.user)
    
    def perform_create(self, serializer):
        """Set the owner of the note to the current authenticated user."""
        serializer.save(owner=self.request.user)