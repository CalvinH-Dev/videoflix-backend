from django.apps import AppConfig


class VideoAppConfig(AppConfig):
    name = "video_app"

    def ready(self):
        from .api import signals
