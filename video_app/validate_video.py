import os

from django.core.exceptions import ValidationError


def validate_video_file(value):
    allowed = [".mp4", ".webm", ".mov", ".mkv"]
    ext = os.path.splitext(value.name)[1].lower()
    if ext not in allowed:
        raise ValidationError(
            f"Nur folgende Formate erlaubt: {', '.join(allowed)}"
        )
