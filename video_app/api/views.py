import os

from django.conf import settings
from django.http import FileResponse, Http404
from rest_framework.generics import ListAPIView, RetrieveAPIView

from video_app.models import Video

from .serializers import VideoSerializer


class VideoListView(ListAPIView):
    queryset = Video.objects.filter(hls_ready=True)
    serializer_class = VideoSerializer


class M3U8View(RetrieveAPIView):
    def retrieve(self, request, movie_id, resolution, *args, **kwargs):
        path = os.path.join(
            settings.MEDIA_ROOT, "hls", str(movie_id), resolution, "index.m3u8"
        )
        if not os.path.exists(path):
            raise Http404
        return FileResponse(
            open(path, "rb"), content_type="application/vnd.apple.mpegurl"
        )


class SegmentView(RetrieveAPIView):
    def retrieve(
        self, request, movie_id, resolution, segment, *args, **kwargs
    ):
        path = os.path.join(
            settings.MEDIA_ROOT, "hls", str(movie_id), resolution, segment
        )
        if not os.path.exists(path):
            raise Http404
        return FileResponse(open(path, "rb"), content_type="video/MP2T")
