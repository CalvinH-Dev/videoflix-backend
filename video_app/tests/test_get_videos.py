from unittest.mock import MagicMock, patch

from django.contrib.auth import get_user_model
from django.core.files.uploadedfile import SimpleUploadedFile
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase

from video_app.models import Video

User = get_user_model()


class VideoListViewTest(APITestCase):
    @patch("video_app.api.signals.get_queue")
    def setUp(self, mock_get_queue):
        mock_queue = MagicMock()
        mock_get_queue.return_value = mock_queue
        self.url = reverse("video-list")

        self.user = User.objects.create_user(
            username="test@example.com",
            email="test@example.com",
            password="securepassword",
        )

        self.video_file = SimpleUploadedFile(
            "video.mp4", b"file_content", content_type="video/mp4"
        )

        self.video1 = Video.objects.create(
            title="Video 1",
            description="Desc 1",
            category="Test",
            original_file=self.video_file,
            hls_ready=True,
        )

        self.video2 = Video.objects.create(
            title="Video 2",
            description="Desc 2",
            category="Test",
            original_file=self.video_file,
            hls_ready=True,
        )

        self.video_not_ready = Video.objects.create(
            title="Video 3",
            description="Desc 3",
            category="Test",
            original_file=self.video_file,
            hls_ready=False,
        )

    def test_unauthenticated_401(self):
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_authenticated_200(self):
        self.client.force_authenticate(user=self.user)
        response = self.client.get(self.url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_only_hls_ready_videos_returned(self):
        self.client.force_authenticate(user=self.user)
        response = self.client.get(self.url)

        ids = [video["id"] for video in response.data]

        self.assertIn(self.video1.id, ids)
        self.assertIn(self.video2.id, ids)
        self.assertNotIn(self.video_not_ready.id, ids)

    def test_video_fields_present(self):
        self.client.force_authenticate(user=self.user)
        response = self.client.get(self.url)

        video = response.data[0]

        self.assertIn("id", video)
        self.assertIn("created_at", video)
        self.assertIn("title", video)
        self.assertIn("description", video)
        self.assertIn("thumbnail_url", video)
        self.assertIn("category", video)

    def test_thumbnail_url_generated(self):
        thumbnail_video = Video.objects.create(
            title="With Thumbnail",
            description="Desc",
            category="Test",
            original_file=self.video_file,
            hls_ready=True,
            thumbnail="thumb.jpg",
        )

        self.client.force_authenticate(user=self.user)
        response = self.client.get(self.url)

        found = next(v for v in response.data if v["id"] == thumbnail_video.id)

        self.assertIsNotNone(found["thumbnail_url"])
        self.assertTrue(found["thumbnail_url"].startswith("http"))

    def test_empty_list(self):
        Video.objects.all().delete()

        self.client.force_authenticate(user=self.user)
        response = self.client.get(self.url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data, [])
