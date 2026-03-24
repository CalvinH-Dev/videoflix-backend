from django.conf import settings
from django.contrib import admin
from django.utils.html import format_html

from .models import Video


@admin.register(Video)
class VideoAdmin(admin.ModelAdmin):
    list_display = [
        "id",
        "title",
        "category",
        "hls_ready",
        "thumbnail_preview",
        "created_at",
    ]
    list_filter = ["hls_ready", "category"]
    search_fields = ["title", "description"]
    readonly_fields = ["hls_ready", "created_at", "thumbnail_preview"]

    def thumbnail_preview(self, obj):
        if obj.thumbnail:
            return format_html(
                '<img src="{}{}" style="height: 60px; border-radius: 4px;"/>',
                settings.MEDIA_URL,
                obj.thumbnail,
            )
        return "-"

    thumbnail_preview.short_description = "Vorschau"
