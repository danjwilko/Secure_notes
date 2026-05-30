from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import (
    PasswordChangeForm,
    SetPasswordForm,
)
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
            # Log the user in and redirect to the home page.
            login(request, new_user)
            return redirect("secure_notes:index")

    # Display a blank or invalid form.
    context = {"form": form}

    return render(request, "registration/register.html", context)

# User requests password reset flow.
class CustomPasswordResetView(PasswordResetView):
    """Custom password reset view that uses our custom form and template"""

    template_name = "registration/password_reset.html"
    email_template_name = "registration/password_reset_email.html"
    success_url = reverse_lazy("accounts:password_reset_done")
class CustomPasswordResetDoneView(PasswordResetDoneView):
    """Custom password reset done view that uses our custom template"""

    template_name = "registration/password_reset_done.html"
class CustomPasswordResetConfirmView(PasswordResetConfirmView):
    """Custom password reset confirm view that uses our custom
    form and template"""

    template_name = "registration/password_reset_confirm.html"
    form_class = SetPasswordForm
    success_url = reverse_lazy("accounts:password_reset_complete")
class CustomPasswordResetCompleteView(PasswordResetCompleteView):
    """Custom password reset complete view that uses our custom template"""

    template_name = "registration/password_reset_complete.html"
    

# User requests password change flow.
class CustomChangePasswordView(LoginRequiredMixin, PasswordChangeView):
    """Custom password change view for logged in users that uses 
    our custom form and template"""

    template_name = "registration/password_change.html"
    form_class = PasswordChangeForm
    success_url = reverse_lazy("secure_notes:index")

class CustomChangePasswordDoneView(LoginRequiredMixin,PasswordChangeDoneView):
    """Custom password change done view for logged in users that uses
    our custom template"""
    template_name = "registration/password_change_done.html"
    success_url = reverse_lazy("secure_notes:index")

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
                user.delete()
                logout(request)

                return redirect("accounts:login")

            form.add_error(None, "Invalid username or password.")

    else:
        form = ReauthenticateForm()

    context = {"form": form}
    return render(request, "registration/delete_account.html", context)
