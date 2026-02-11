from django import forms

from .models import Note

class NoteForm(forms.ModelForm):
    """Form for creating and updating notes."""
    
    class Meta:
        model = Note
        fields = ['title', 'content']
        labels = {
            'title': 'Note Title',
            'content': 'Note Text',
        }
        widgets = {
            'title': forms.TextInput(attrs={'class': 'form-control'}),
            'content': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 20}),
        }