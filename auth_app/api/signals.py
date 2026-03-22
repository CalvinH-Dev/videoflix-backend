# signals.py
import secrets

from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.utils.encoding import force_bytes
from django.utils.http import urlsafe_base64_encode

from auth_app.api.tasks import send_activation_email
from core.redis_client import get_connection, get_queue

q = get_queue()
r = get_connection()


@receiver(post_save, sender=User)
def send_activation_on_register(sender, instance, created, **kwargs):
    if created and not instance.is_active:
        token = secrets.token_urlsafe(32)
        uid = urlsafe_base64_encode(force_bytes(instance.pk))

        q.enqueue(send_activation_email, instance.email, uid, token)
