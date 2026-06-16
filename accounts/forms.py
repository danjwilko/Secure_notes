from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User


class SecureUserCreationForm(UserCreationForm):
    """
    Form for creating new users with an email field.
    Password validation is enforced via Django's AUTH_PASSWORD_VALIDATORS.
    """

    email = forms.EmailField(
        required=True, help_text="Required. Enter a valid email address."
    )

    class Meta:
        model = User
        fields = ("username", "email", "password1", "password2")

    def clean_email(self):
        email = self.cleaned_data.get("email").lower()
        if User.objects.filter(email=email).exists():
            raise forms.ValidationError(
                "A user with that email already exists."
            )
        return email


class ReauthenticateForm(forms.Form):
    """Form for authenticating users before account deletion."""

    username = forms.CharField(
        max_length=150,
        widget=forms.TextInput(attrs={"class": "form-control"}),
    )
    password = forms.CharField(
        widget=forms.PasswordInput(attrs={"class": "form-control"})
    )
