from django.db import models

from video_app.validate_video import validate_video_file


class Video(models.Model):
    title = models.CharField(max_length=255)
    description = models.TextField()
    thumbnail = models.CharField(max_length=255, blank=True)
    category = models.CharField(max_length=100)

    original_file = models.FileField(
        upload_to="originals/", validators=[validate_video_file]
    )
    hls_ready = models.BooleanField(default=False)

    created_at = models.DateTimeField(auto_now_add=True)
