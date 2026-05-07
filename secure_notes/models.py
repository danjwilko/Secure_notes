from django.conf import settings
from django.db import models


class Note(models.Model):
    """Model representing a secure note."""

    owner = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="notes",
    )  # Switched to settings.AUTH_USER_MODEL for custom user
    # model compatibility
    title = models.CharField(max_length=255)
    content = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-created_at"]
        constraints = [
            models.UniqueConstraint(
                fields=["owner", "title"], name="unique_note_title_per_user"
            )
        ]

    def __str__(self):
        return self.title
