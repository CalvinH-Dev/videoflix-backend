from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.dispatch import receiver

from auth_app.api.helpers import create_token_and_uid_for_user
from auth_app.api.tasks import send_activation_email
from auth_app.models import ActivationToken
from core.redis_client import get_queue

try:
    q = get_queue()
except Exception:
    q = None


@receiver(post_save, sender=User)
def send_activation_on_register(sender, instance, created, **kwargs):
    if created and not instance.is_active:
        token, uid = create_token_and_uid_for_user(instance)

        ActivationToken.objects.create(user=instance, token=token)
        queue = q or get_queue()
        queue.enqueue(send_activation_email, instance.email, uid, token)
