from django.urls import path

from .views import M3U8View, SegmentView, VideoListView

urlpatterns = [
    path("video/", VideoListView.as_view()),
    path(
        "video/<int:movie_id>/<str:resolution>/index.m3u8", M3U8View.as_view()
    ),
    path(
        "video/<int:movie_id>/<str:resolution>/<str:segment>/",
        SegmentView.as_view(),
    ),
]
