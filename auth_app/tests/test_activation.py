from datetime import timedelta
from unittest.mock import MagicMock, patch

from django.contrib.auth import get_user_model
from django.urls import reverse
from django.utils import timezone
from django.utils.encoding import force_bytes
from django.utils.http import urlsafe_base64_encode
from rest_framework import status
from rest_framework.test import APITestCase

from auth_app.models import ActivationToken

User = get_user_model()


class ActivateAccountViewTest(APITestCase):
    @patch("auth_app.api.signals.q")
    def setUp(self, mock_queue):
        mock_queue.enqueue = MagicMock()
        self.user = User.objects.create_user(
            username="test@example.com",
            email="test@example.com",
            password="securepassword",
            is_active=False,
        )
        self.token_value = "validtoken123"
        ActivationToken.objects.filter(user=self.user).delete()
        self.activation = ActivationToken.objects.create(
            user=self.user, token=self.token_value
        )
        self.uid = urlsafe_base64_encode(force_bytes(self.user.pk))
        self.url = reverse(
            "activate", kwargs={"uidb64": self.uid, "token": self.token_value}
        )

    def test_valid_activation_200(self):
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn("detail", response.data)
        self.user.refresh_from_db()
        self.assertTrue(self.user.is_active)
        self.assertFalse(
            ActivationToken.objects.filter(user=self.user).exists()
        )

    def test_invalid_uid_400(self):
        url = reverse(
            "activate",
            kwargs={"uidb64": "invalid!!", "token": self.token_value},
        )
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("detail", response.data)

    def test_nonexistent_user_400(self):
        uid = urlsafe_base64_encode(force_bytes(99999))
        url = reverse(
            "activate", kwargs={"uidb64": uid, "token": self.token_value}
        )
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("detail", response.data)

    def test_wrong_token_400(self):
        url = reverse(
            "activate", kwargs={"uidb64": self.uid, "token": "wrong_token"}
        )
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("detail", response.data)

    def test_already_used_token_400(self):
        self.client.get(self.url)
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_expired_token_400(self):
        self.activation.created_at = timezone.now() - timedelta(hours=25)
        self.activation.save()
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("detail", response.data)

    def test_expired_token_gets_deleted(self):
        self.activation.created_at = timezone.now() - timedelta(hours=25)
        self.activation.save()
        self.client.get(self.url)
        self.assertFalse(
            ActivationToken.objects.filter(user=self.user).exists()
        )
