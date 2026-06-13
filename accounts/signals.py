import logging

from django.contrib.auth.signals import (
    user_logged_in,
    user_logged_out,
    user_login_failed,
)
from django.dispatch import receiver

logger = logging.getLogger(__name__)

@receiver(user_logged_in)
def log_user_login(sender, request, user, **kwargs):
    if user is None:
        logger.warning("Login signal received with no authenticated user.")
    else:
        logger.info("User logged in: id=%s username=%s",
        user.id,
        user.username,
        )

@receiver(user_logged_out)
def log_user_logout(sender, request, user, **kwargs):
    if user is None:
        logger.warning("Logout signal received with no authenticated user.")
    else:
        logger.info("User logged out: id=%s username=%s",
                       user.id,
                   user.username,
    )

@receiver(user_login_failed)
def log_user_failed(sender, credentials, request, **kwargs):
    logger.warning(
        "Failed login attempt for username: %s",
        credentials.get("username", "unknown"),
    )