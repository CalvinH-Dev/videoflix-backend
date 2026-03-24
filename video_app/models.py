from django.db import models


class Video(models.Model):
    title = models.CharField(max_length=255)
    description = models.TextField()
    thumbnail = models.ImageField(upload_to="thumbnails/")
    category = models.CharField(max_length=100)

    original_file = models.FileField(upload_to="originals/")
    hls_ready = models.BooleanField(default=False)

    created_at = models.DateTimeField(auto_now_add=True)
