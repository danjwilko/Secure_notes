from django.urls import path

from .views import PrivacyPolicyView

app_name = "legal"

urlpatterns = [
    path(
        "privacy-policy/", PrivacyPolicyView.as_view(), name="privacy_policy"
    ),
]
