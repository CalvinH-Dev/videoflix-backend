import json
import subprocess


def get_video_duration(path: str) -> float:
    """
    Retrieve the duration of a video file in seconds using ffprobe.

    Args:
        path: Path to the video file.

    Returns:
        Duration of the video in seconds as a float.
    """
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


def get_video_dimensions(input_path: str) -> tuple[int, int]:
    """
    Retrieve the width and height of a video file using ffprobe.

    Args:
        input_path: Path to the video file.

    Returns:
        Tuple of (width, height) as integers.
    """
    result = subprocess.run(
        [
            "ffprobe",
            "-v",
            "error",
            "-select_streams",
            "v:0",
            "-show_entries",
            "stream=width,height",
            "-of",
            "csv=p=0",
            input_path,
        ],
        capture_output=True,
        text=True,
    )
    width, height = map(int, result.stdout.strip().split(","))
    return width, height
