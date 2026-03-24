import os

from django.core.exceptions import ValidationError


def validate_video_file(value):
    """
    Validate that the uploaded file has an allowed video extension.

    Args:
        value: Uploaded file object.

    Raises:
        ValidationError: If the file extension is not in the allowed list.
    """
    allowed = [".mp4", ".webm", ".mov", ".mkv"]
    ext = os.path.splitext(value.name)[1].lower()
    if ext not in allowed:
        raise ValidationError(
            f"Only the following formats are allowed: {', '.join(allowed)}"
        )
