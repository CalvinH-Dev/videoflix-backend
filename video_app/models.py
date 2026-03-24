from django.db import models

from video_app.validate_video import validate_video_file


class Video(models.Model):
    """
    Model representing a video uploaded to the platform.

    Attributes:
        title: Title of the video.
        description: Description of the video content.
        thumbnail: Optional thumbnail image path or URL.
        category: Category or genre of the video.
        original_file: Uploaded video file, validated for allowed formats.
        hls_ready: Boolean indicating if HLS conversion is complete.
        created_at: Timestamp when the video was created.
    """

    title = models.CharField(max_length=255)
    description = models.TextField()
    thumbnail = models.CharField(max_length=255, blank=True)
    category = models.CharField(max_length=100)

    original_file = models.FileField(
        upload_to="originals/", validators=[validate_video_file]
    )
    hls_ready = models.BooleanField(default=False)

    created_at = models.DateTimeField(auto_now_add=True)
