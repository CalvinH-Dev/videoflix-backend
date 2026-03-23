from unittest.mock import MagicMock, patch

from django.contrib.auth import get_user_model
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase

User = get_user_model()


class ResetPasswordViewTest(APITestCase):
    @patch("auth_app.api.signals.q")
    def setUp(self, mock_queue):
        mock_queue.enqueue = MagicMock()
        self.user = User.objects.create_user(
            username="test@example.com",
            email="test@example.com",
            password="securepassword",
            is_active=True,
        )
        self.url = reverse("reset-password")

    def test_valid_email_200(self):
        response = self.client.post(self.url, {"email": self.user.email})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn("detail", response.data)

    def test_nonexistent_email_still_200(self):
        response = self.client.post(self.url, {"email": "ghost@example.com"})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual("detail", response.data)

    def test_missing_email_400(self):
        response = self.client.post(self.url, {})
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual("detail", response.data)

    @patch("auth_app.api.views.get_queue")
    def test_email_job_enqueued(self, mock_get_queue):
        mock_queue = MagicMock()
        mock_get_queue.return_value = mock_queue
        self.client.post(self.url, {"email": self.user.email})
        mock_queue.enqueue.assert_called_once()

    @patch("auth_app.api.views.get_queue")
    def test_no_job_enqueued_for_unknown_email(self, mock_get_queue):
        mock_queue = MagicMock()
        mock_get_queue.return_value = mock_queue
        self.client.post(self.url, {"email": "ghost@example.com"})
        mock_queue.enqueue.assert_not_called()

    def test_empty_email_string_400(self):
        response = self.client.post(self.url, {"email": ""})
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual("detail", response.data)
