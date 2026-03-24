from datetime import datetime, timedelta
from typing import cast

from django.contrib.auth.models import User
from django.db import models
from django.utils import timezone


class ActivationToken(models.Model):
    user = models.OneToOneField(
        User, on_delete=models.CASCADE, related_name="activation_token"
    )
    token = models.CharField(max_length=64)
    created_at = models.DateTimeField(auto_now_add=True)

    def is_expired(self) -> bool:
        created_at = cast(datetime | None, self.created_at)

        if not created_at:
            return False

        return timezone.now() > created_at + timedelta(hours=24)
