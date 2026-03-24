from datetime import datetime, timedelta
from typing import cast

from django.contrib.auth.models import User
from django.db import models
from django.utils import timezone


class ActivationToken(models.Model):
    """
    Model representing an activation token associated with a user.

    Attributes:
        user (User): The user associated with this activation token.
        token (str): The unique token string used for activation.
        created_at (datetime): Timestamp when the token was created.
    """

    user = models.OneToOneField(
        User, on_delete=models.CASCADE, related_name="activation_token"
    )
    token = models.CharField(max_length=64)
    created_at = models.DateTimeField(auto_now_add=True)

    def is_expired(self) -> bool:
        """
        Check if the activation token has expired.

        Returns:
            bool: True if the token is expired (older than 24 hours), False otherwise.
        """
        created_at = cast(datetime | None, self.created_at)

        if not created_at:
            return False

        return timezone.now() > created_at + timedelta(hours=24)
