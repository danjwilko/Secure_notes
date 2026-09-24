import pytest
from django.contrib.auth import get_user_model
from django.core.cache import cache
from rest_framework.test import APIClient
from rest_framework_simplejwt.tokens import RefreshToken


@pytest.fixture(autouse=True)
def clear_test_cache():
    """Prevent cached rate-limit state leaking between tests."""
    cache.clear()
    yield
    cache.clear()


@pytest.fixture
def user(db):
    """Create an active test user."""
    User = get_user_model()

    return User.objects.create_user(
        username="testuser",
        password="testpass",
    )


@pytest.fixture
def api_client():
    """Return a factory for authenticated API clients."""

    def make_client(user):
        client = APIClient()
        refresh = RefreshToken.for_user(user)

        client.credentials(
            HTTP_AUTHORIZATION=f"Bearer {refresh.access_token}"
        )
        return client

    return make_client
