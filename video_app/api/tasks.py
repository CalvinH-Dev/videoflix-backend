import os
import subprocess

from django.conf import settings

from video_app.api.helpers import get_video_duration


def generate_thumbnail(video_id, input_path, duration):
    thumbnail_dir = os.path.join(settings.MEDIA_ROOT, "thumbnail")
    os.makedirs(thumbnail_dir, exist_ok=True)
    thumbnail_path = os.path.join(thumbnail_dir, f"{video_id}.webp")

    timestamp = "00:00:05" if duration > 10 else "00:00:01"

    result = subprocess.run(
        [
            "ffmpeg",
            "-i",
            input_path,
            "-ss",
            timestamp,
            "-vframes",
            "1",
            "-vf",
            "scale=1280:720",
            thumbnail_path,
        ]
    )

    return result.returncode == 0


def generate_hls(video_id, input_path):
    resolutions = {
        "1080p": ("1920x1080", "5000k"),
        "720p": ("1280x720", "2800k"),
        "480p": ("854x480", "1400k"),
    }

    for res_name, (size, bitrate) in resolutions.items():
        output_dir = os.path.join(
            settings.MEDIA_ROOT, "hls", str(video_id), res_name
        )
        os.makedirs(output_dir, exist_ok=True)

        result = subprocess.run(
            [
                "ffmpeg",
                "-i",
                input_path,
                "-s",
                size,
                "-b:v",
                bitrate,
                "-hls_time",
                "10",
                "-hls_list_size",
                "0",
                "-f",
                "hls",
                f"{output_dir}/index.m3u8",
            ]
        )

        if result.returncode != 0:
            return False

    return True


def convert_to_hls(video_id):
    from video_app.models import Video

    if not Video.objects.filter(id=video_id).exists():
        return

    video = Video.objects.get(id=video_id)

    if not video.original_file:
        return

    input_path = video.original_file.path
    duration = get_video_duration(input_path)

    if not generate_thumbnail(video_id, input_path, duration):
        return

    if not generate_hls(video_id, input_path):
        return

    video.hls_ready = True
    video.save()
