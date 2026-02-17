from rest_framework import serializers
from .models import Note
    
class NoteSerializer(serializers.ModelSerializer):
    """Serializer for the Note model."""
        
    class Meta:
        model = Note
        fields = ['id', 'title', 'content', 'created_at', 'updated_at']
        read_only_fields = ['created_at', 'updated_at']
        
    def validate_title(self, value):
        request = self.context.get("request")
        if not request or not request.user.is_authenticated:
            return value  # Skip validation for unauthenticated users (should be handled by permissions)
        
        # Get all notes with the same title for the current user
        qs = Note.objects.filter(owner=request.user, title=value)

        # If updating, exclude the current instance
        if self.instance is not None:
            qs = qs.exclude(pk=self.instance.pk)

        if qs.exists():
            raise serializers.ValidationError(
                "You already have a note with this title."
            )

        return value
