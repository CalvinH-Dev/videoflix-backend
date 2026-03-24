import os
import subprocess


def convert_to_hls(video_id):
    from video_app.models import Video

    if not Video.objects.filter(id=video_id).exists():
        return

    video = Video.objects.get(id=video_id)

    if not video.original_file:
        return

    resolutions = {
        "1080p": ("1920x1080", "5000k"),
        "720p": ("1280x720", "2800k"),
        "480p": ("854x480", "1400k"),
    }

    for res_name, (size, bitrate) in resolutions.items():
        output_dir = f"media/hls/{video_id}/{res_name}"
        os.makedirs(output_dir, exist_ok=True)

        result = subprocess.run(
            [
                "ffmpeg",
                "-i",
                video.original_file.path,
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
            return

    video.hls_ready = True
    video.save()
