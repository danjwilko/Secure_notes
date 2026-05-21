from django import forms

from .models import Note


class NoteForm(forms.ModelForm):
    """Form for creating and updating notes."""

    def __init__(self, *args, user=None, **kwargs):
        super().__init__(*args, **kwargs)
        self.user = user

    def clean_title(self):
        """Prevent duplicate note titles for the same user."""
        title = self.cleaned_data["title"]

        if self.user is None:
            return title

        qs = Note.objects.filter(owner=self.user, title=title)

        if self.instance.pk:
            qs = qs.exclude(pk=self.instance.pk)

        if qs.exists():
            raise forms.ValidationError(
                "You already have a note with this title."
            )

        return title


    class Meta:
        model = Note
        fields = ["title", "content"]
        labels = {
            "title": "Note Title",
            "content": "Note Text",
        }
        widgets = {
            "title": forms.TextInput(attrs={"class": "form-control"}),
            "content": forms.Textarea(
                attrs={"class": "form-control", "rows": 20}
            ),
        }
