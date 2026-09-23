import logging

from django.conf import settings
from django.core import signing
from django.core.mail import EmailMultiAlternatives
from django.template import loader
from django.urls import reverse

logger = logging.getLogger(__name__)


VERIFY_EMAIL_SALT = "accounts.email-verification.v1"

def send_verification_email(request, user):
    """Send an email to the user to verify their
    email address. before completing registration."""

    token = signing.dumps(user.pk, salt=VERIFY_EMAIL_SALT)

    verify_url = request.build_absolute_uri(
        reverse("accounts:verify_email", args=[token])
    )

    subject = "Verify your email address"
    subject = "".join(subject.splitlines())
    from_email = settings.DEFAULT_FROM_EMAIL
    to_email = user.email

    context = {
        "user": user,
        "verify_url": verify_url,
    }

    body = loader.render_to_string(
        "registration/verification_email.txt", context
    )
    html_content = loader.render_to_string(
        "registration/verification_email.html", context
    )

    email_message = EmailMultiAlternatives(
        subject,
        body,
        from_email,
        [to_email]
    )
    if html_content is not None:
        email_message.attach_alternative(
            html_content,
            "text/html")

    try:
        return bool(email_message.send())
    except Exception:
        logger.exception(
            "Failed to send verification email to ID %s",
            user.pk,
            )
        return False
