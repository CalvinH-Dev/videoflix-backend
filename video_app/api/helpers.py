import json
import subprocess


def get_video_duration(path):
    result = subprocess.run(
        [
            "ffprobe",
            "-v",
            "quiet",
            "-print_format",
            "json",
            "-show_format",
            path,
        ],
        capture_output=True,
        text=True,
    )

    data = json.loads(result.stdout)
    return float(data["format"]["duration"])
