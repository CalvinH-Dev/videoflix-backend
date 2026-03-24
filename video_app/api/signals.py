from django.db.models.signals import post_save
from django.dispatch import receiver

from core.redis_client import get_queue
from video_app.models import Video

from .tasks import convert_to_hls

try:
    q = get_queue()
except Exception:
    q = None


@receiver(post_save, sender=Video)
def on_video_created(sender, instance, created, **kwargs):
    if not created:
        return

    if not instance.thumbnail:
        instance.thumbnail = f"thumbnail/{instance.pk}.webp"
        instance.save()

    if instance.original_file:
        queue = q or get_queue()
        queue.enqueue(convert_to_hls, instance.id)
