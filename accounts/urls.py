"""Defines the URL patterns for the accounts app."""

from django.contrib.auth import views as auth_views
from django.urls import include, path

from . import views

app_name = "accounts"
urlpatterns = [
    # Registaration page.
    path("register/", views.register, name="register"),
    # Default auth urls for login and logout.
    #Login
    path("login/", auth_views.LoginView.as_view(), name="login"),
    # Logout
    path("logout/", auth_views.LogoutView.as_view(), name="logout"),
    # Custom password reset - Uses Django's built-in views but with
    # custom templates and forms.
    # Password reset on login flow:
    # Password reset request page.
    path(
        "password_reset/",
        views.CustomPasswordResetView.as_view(),
        name="password_reset",
    ),
    # Password reset confirm page
    path(
        "password_reset_confirm/<uidb64>/<token>/",
        views.CustomPasswordResetConfirmView.as_view(),
        name="password_reset_confirm",
    ),
    # Password reset done page.
    path(
        "password_reset_done/",
        views.CustomPasswordResetDoneView.as_view(),
        name="password_reset_done",
    ),
    # Password reset complete page.
    path(
        "password_reset_complete/",
        views.CustomPasswordResetCompleteView.as_view(),
        name="password_reset_complete",
    ),
    # Logged in user password change.
    path(
        "password_change/",
        views.CustomChangePasswordView.as_view(),
        name="password_change",
    ),
    # redirect the user to the dashboard on cancel/successful password change
    path(
        "password_change_done/",
        views.CustomChangePasswordDoneView.as_view(),
        name="password_change_done",
    ),
    # Account deletion views
    path(
        "delete_account/",
        views.delete_account,
        name="delete_account",
    ),
]
