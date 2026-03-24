import os

from django.conf import settings
from django.http import FileResponse, Http404
from rest_framework.generics import ListAPIView, RetrieveAPIView

from video_app.models import Video

from .serializers import VideoSerializer


class VideoListView(ListAPIView):
    """
    API view to list all videos that are ready for streaming (HLS-ready).

    Attributes:
        queryset: Videos filtered by hls_ready=True.
        serializer_class: Serializer used to convert Video instances.
    """

    queryset = Video.objects.filter(hls_ready=True)
    serializer_class = VideoSerializer


class M3U8View(RetrieveAPIView):
    """
    API view to retrieve the HLS playlist (.m3u8) file for a video.
    """

    def retrieve(
        self, request, movie_id: int, resolution: str, *args, **kwargs
    ):
        """
        Return the .m3u8 playlist file for a specific video and resolution.

        Args:
            request: Incoming HTTP request.
            movie_id: ID of the video.
            resolution: Resolution folder (e.g., '720p').

        Returns:
            FileResponse containing the .m3u8 playlist.

        Raises:
            Http404: If the playlist file does not exist.
        """
        path = os.path.join(
            settings.MEDIA_ROOT, "hls", str(movie_id), resolution, "index.m3u8"
        )
        if not os.path.exists(path):
            raise Http404
        return FileResponse(
            open(path, "rb"), content_type="application/vnd.apple.mpegurl"
        )


class SegmentView(RetrieveAPIView):
    """
    API view to retrieve individual HLS video segments.
    """

    def retrieve(
        self,
        request,
        movie_id: int,
        resolution: str,
        segment: str,
        *args,
        **kwargs,
    ):
        """
        Return a specific video segment file for a given video and resolution.

        Args:
            request: Incoming HTTP request.
            movie_id: ID of the video.
            resolution: Resolution folder (e.g., '720p').
            segment: Segment file name (e.g., 'segment1.ts').

        Returns:
            FileResponse containing the video segment.

        Raises:
            Http404: If the segment file does not exist.
        """
        path = os.path.join(
            settings.MEDIA_ROOT, "hls", str(movie_id), resolution, segment
        )
        if not os.path.exists(path):
            raise Http404
        return FileResponse(open(path, "rb"), content_type="video/MP2T")
