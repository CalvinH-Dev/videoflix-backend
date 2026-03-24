from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.dispatch import receiver

from auth_app.api.helpers import create_token_and_uid_for_user
from auth_app.api.tasks import send_activation_email
from auth_app.models import ActivationToken
from core.redis_client import get_queue

try:
    q = get_queue("high")
except Exception:
    q = None


@receiver(post_save, sender=User)
def send_activation_on_register(
    sender, instance: User, created: bool, **kwargs
):
    """
    Send an activation email to the user after registration.

    This function is triggered after a User instance is saved. If the user
    was newly created and is inactive, an activation token is generated
    and a task is enqueued to send the activation email.

    Args:
        sender: The model class (User) sending the signal.
        instance: The User instance that was saved.
        created: Boolean indicating whether a new instance was created.
        **kwargs: Additional keyword arguments.
    """
    if created and not instance.is_active:
        token, uid = create_token_and_uid_for_user(instance)
        ActivationToken.objects.create(user=instance, token=token)
        queue = q or get_queue("high")
        queue.enqueue(send_activation_email, instance.email, uid, token)
