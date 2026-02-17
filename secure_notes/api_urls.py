"""Define URL patterns for the api endpoints of the secure_notes app."""
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .api import NoteViewSet

router = DefaultRouter()
router.register(r'notes', NoteViewSet, basename='note')


urlpatterns = [
    path('', include(router.urls)),
]
