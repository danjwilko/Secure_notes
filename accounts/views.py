import logging

from django.contrib.auth import authenticate, get_user_model, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import PasswordChangeForm, SetPasswordForm
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.views import (
    PasswordChangeDoneView,
    PasswordChangeView,
    PasswordResetCompleteView,
    PasswordResetConfirmView,
    PasswordResetDoneView,
    PasswordResetView,
)
from django.shortcuts import redirect, render
from django.urls import reverse_lazy

from .forms import ReauthenticateForm, SecureUserCreationForm

logger = logging.getLogger(__name__)


def mask_email(email):
    if not email or "@" not in email:
        return "invalid-email"

    name, domain = email.split("@", 1)

    if len(name) <= 2:
        masked_name = name[0] + "***"
    else:
        masked_name = name[:2] + "***"

    return f"[{masked_name}@{domain}]"


def register(request):
    """View function to handle user registration."""
    if request.method != "POST":
        # Display a blank registration form.
        form = SecureUserCreationForm()
    else:
        # Process the submitted form data.
        form = SecureUserCreationForm(request.POST)
        if form.is_valid():
            new_user = form.save()
            logger.info("New user registered: %s", new_user.username)
            # Log the user in and redirect to the home page.
            login(request, new_user)
            logger.info(
                "User logged in after registration: %s", new_user.username
            )
            return redirect("secure_notes:index")

    # Display a blank or invalid form.
    context = {"form": form}

    return render(request, "registration/register.html", context)


# User requests password reset flow.
class CustomPasswordResetView(PasswordResetView):
    """Handles the password reset email requests."""

    template_name = "registration/password_reset.html"
    email_template_name = "registration/password_reset_email.html"
    success_url = reverse_lazy("accounts:password_reset_done")

    def form_valid(self, form):
        """Log the password reset request for auditing purposes."""

        email = form.cleaned_data.get("email")
        masked_email = mask_email(email)

        User = get_user_model()
        user_exists = User.objects.filter(email__iexact=email).exists()

        logger.info(
            "Password reset requested for email=%s user_exists=%s",
            masked_email,
            user_exists,
        )

        return super().form_valid(form)


class CustomPasswordResetDoneView(PasswordResetDoneView):
    """Displays confirmation that apassword reset email has been sent."""

    template_name = "registration/password_reset_done.html"


class CustomPasswordResetConfirmView(PasswordResetConfirmView):
    """Handles setting a new password from a reset link"""

    template_name = "registration/password_reset_confirm.html"
    form_class = SetPasswordForm
    success_url = reverse_lazy("accounts:password_reset_complete")

    def form_valid(self, form):
        """Log successful password reset."""
        logger.info("Password reset completed for user=%s", self.user.username)
        return super().form_valid(form)


class CustomPasswordResetCompleteView(PasswordResetCompleteView):
    """Displays a confirmation message that the password reset is complete."""

    template_name = "registration/password_reset_complete.html"


# User requests password change flow.
class CustomChangePasswordView(LoginRequiredMixin, PasswordChangeView):
    """Handles the password changes for logged in users."""

    template_name = "registration/password_change.html"
    form_class = PasswordChangeForm
    success_url = reverse_lazy("accounts:password_change_done")

    def form_valid(self, form):
        """Log successful password changes."""
        logger.info("Password changed user=%s", self.request.user.username)
        return super().form_valid(form)


class CustomChangePasswordDoneView(LoginRequiredMixin, PasswordChangeDoneView):
    """Custom password change done view for logged in users that uses
    our custom template"""

    template_name = "registration/password_change_done.html"


@login_required
def delete_account(request):
    """View function to handle account deletion."""

    if request.method == "POST":
        form = ReauthenticateForm(request.POST)

        if form.is_valid():
            username = form.cleaned_data["username"]
            password = form.cleaned_data["password"]
            user = authenticate(request, username=username, password=password)

            if user is not None and user == request.user:
                username = user.username
                user_id = user.id
                logger.warning(
                    "User account deleted username=%s user_id=%s",
                    username,
                    user_id,
                )
                logout(request)
                user.delete()

                return redirect("accounts:login")

            logger.warning(
                "Failed account deletion attempt "
                "request_user=%s submitted_username=%s",
                request.user.username,
                username,
            )
            form.add_error(None, "Invalid username or password.")

    else:
        form = ReauthenticateForm()

    context = {"form": form}
    return render(request, "registration/delete_account.html", context)
