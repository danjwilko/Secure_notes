import logging

from django.contrib.auth import authenticate, get_user_model, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import PasswordChangeForm, SetPasswordForm
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.views import (
    LoginView,
    PasswordChangeDoneView,
    PasswordChangeView,
    PasswordResetCompleteView,
    PasswordResetConfirmView,
    PasswordResetDoneView,
    PasswordResetView,
)
from django.core import signing
from django.shortcuts import redirect, render
from django.urls import reverse_lazy
from django.utils.decorators import method_decorator
from django_ratelimit.decorators import ratelimit, settings

from .email import VERIFY_EMAIL_SALT, send_verification_email
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


@ratelimit(key="ip", rate="5/h", method="POST", block=True)
def register(request):
    """View function to handle user registration, initially set as
    an inactive user and an email verification link is sent"""

    if request.method != "POST":
        # Display a blank registration form.
        form = SecureUserCreationForm()

    else:
        # Process the data - send a link to the users inputted email,
        # set as iactive.
        form = SecureUserCreationForm(request.POST)
        if form.is_valid():
            new_user = form.save(commit=False)
            new_user.email = new_user.email.strip().lower()
            new_user.is_active = False
            new_user.save()

            logger.info(
                "Inactive user ID %s registered and awaits email verification",
                new_user.pk,
            )

            email_sent = send_verification_email(
                request,
                new_user
                )
            if not email_sent:
                logger.warning(
                    "Verification email could not be sent to the user ID %s",
                    new_user.pk,
                )

            return redirect("accounts:verification_sent")

    # Display a blank or invalid form.
    context = {"form": form}

    return render(request, "registration/register.html", context)


User = get_user_model()


def verify_email(request, token):
    try:
        user_pk = signing.loads(
            token,
            salt=VERIFY_EMAIL_SALT,
            max_age=settings.EMAIL_VERIFICATION_TIMEOUT,
        )

    except signing.SignatureExpired:
        return redirect("accounts:verification_expired")

    except signing.BadSignature:
        return redirect("accounts:verification_invalid")

    try:
        user = User.objects.get(pk=user_pk)
    except (User.DoesNotExist, TypeError, ValueError):
        return redirect("accounts:verification_invalid")

    if user.is_active:
        return redirect("accounts:verification_complete")

    user.is_active = True
    user.save(update_fields=["is_active"])

    logger.info(
        "User ID %s completed email verification",
        user_pk,
    )

    return redirect("accounts:verification_complete")



@method_decorator(
    ratelimit(key="ip", rate="5/m", method="POST", block=True), name="dispatch"
)
@method_decorator(
    ratelimit(key="post:username", rate="5/m", method="POST", block=True),
    name="dispatch",
)
class CustomLoginView(LoginView):
    """Custom login view that applies rate limiting
    to prevent brute-force attacks."""

    template_name = "registration/login.html"


# User requests password reset flow.
@method_decorator(
    ratelimit(key="post:email", rate="5/h", method="POST", block=True),
    name="dispatch",
)
class CustomPasswordResetView(PasswordResetView):
    """Handles the password reset email requests."""

    template_name = "registration/password_reset.html"
    email_template_name = "registration/password_reset_email.txt"
    html_email_template_name = "registration/password_reset_email.html"
    subject_template_name = "registration/password_reset_subject.txt"
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
    """Displays confirmation that a password reset email has been sent."""

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
@method_decorator(
    ratelimit(key="user", rate="5/h", method="POST", block=True),
    name="dispatch",
)
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
@ratelimit(key="user", rate="2/h", method="POST", block=True)
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
                user_id = user.pk
                logout(request)
                user.delete()
                logger.warning(
                    "User account deleted username=%s user_id=%s",
                    username,
                    user_id,
                )

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
