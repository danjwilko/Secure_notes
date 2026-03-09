"""Defines the URL patterns for the accounts app."""

from django.urls import include, path

from . import views

app_name = "accounts"
urlpatterns = [
    # Include default auth urls.
    path("", include("django.contrib.auth.urls")),
    # Registaration page.
    path("register/", views.register, name="register"),
]
