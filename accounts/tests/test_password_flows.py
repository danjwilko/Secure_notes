import re

import pytest
from django.urls import reverse


# Tests for password change and reset - (not for API endpoints)
@pytest.mark.django_db
def test_user_can_change_password(client, user):
    assert client.login(username="testuser", password="testpass")

    response = client.post(
        reverse("accounts:password_change"),
        {
            "old_password": "testpass",
            "new_password1": "newstrongpassword123",
            "new_password2": "newstrongpassword123",
        },
    )

    assert response.status_code == 302
    user.refresh_from_db()
    assert user.check_password("newstrongpassword123")


@pytest.mark.django_db
def test_user_can_reset_password(client, user, mailoutbox):
    user.email = "test@test.com"
    user.save(update_fields=["email"])

    # Here we request the reset email.
    response = client.post(
        reverse("accounts:password_reset"),
        {"email": "test@test.com"},
    )

    assert response.status_code == 302
    assert len(mailoutbox) == 1
    assert mailoutbox[0].to == ["test@test.com"]

    email = mailoutbox[0].body
    url_match = re.search(
        r'(/accounts/password_reset_confirm/[^">\s]+)', email
    )
    if url_match is None:
        pytest.fail("Password reset email did not contain the expected url")

    url = url_match.group(1)

    response = client.get(url, follow=True)

    assert response.status_code == 200
    post_url = response.redirect_chain[-1][0]

    response = client.post(
        post_url,
        {
            "new_password1": "newstrongpassword123",
            "new_password2": "newstrongpassword123",
        },
        follow=True,
    )
    assert response.status_code == 200

    user.refresh_from_db()
    assert user.check_password("newstrongpassword123")
