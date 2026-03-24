from rest_framework import serializers

from video_app.models import Video


class VideoSerializer(serializers.ModelSerializer):
    """
    Serializer for the Video model.

    Adds a computed field 'thumbnail_url' to provide the full URL
    for the video's thumbnail image.
    """

    thumbnail_url = serializers.SerializerMethodField()

    class Meta:
        model = Video
        fields = [
            "id",
            "created_at",
            "title",
            "description",
            "thumbnail_url",
            "category",
        ]

    def get_thumbnail_url(self, obj: Video) -> str | None:
        """
        Build absolute URL for the video's thumbnail.

        Args:
            obj: Video instance.

        Returns:
            Full URL string if thumbnail exists, otherwise None.
        """
        request = self.context.get("request")
        if obj.thumbnail and request:
            return request.build_absolute_uri(f"/media/{obj.thumbnail}")
        return None
