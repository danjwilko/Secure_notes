"""Defines the URL patterns for the accounts app."""

from . import views
from django.urls import path, include

app_name = 'accounts'
urlpatterns = [
    # Include default auth urls.
    path('', include('django.contrib.auth.urls')),
    # Registaration page.
    path('register/', views.register, name='register'),
]