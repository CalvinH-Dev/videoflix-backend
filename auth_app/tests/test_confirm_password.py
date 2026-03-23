from unittest.mock import MagicMock, patch

from django.contrib.auth import get_user_model
from django.contrib.auth.tokens import default_token_generator
from django.urls import reverse
from django.utils.encoding import force_bytes
from django.utils.http import urlsafe_base64_encode
from rest_framework import status
from rest_framework.test import APITestCase

User = get_user_model()


class PasswordConfirmViewTest(APITestCase):
    @patch("auth_app.api.signals.q")
    def setUp(self, mock_queue):
        mock_queue.enqueue = MagicMock()
        self.user = User.objects.create_user(
            username="test@example.com",
            email="test@example.com",
            password="oldpassword",
            is_active=True,
        )
        self.uid = urlsafe_base64_encode(force_bytes(self.user.pk))
        self.token = default_token_generator.make_token(self.user)
        self.url = reverse(
            "confirm-password",
            kwargs={"uidb64": self.uid, "token": self.token},
        )
        self.valid_payload = {
            "new_password": "newsecurepassword",
            "confirm_password": "newsecurepassword",
        }

    def test_valid_reset_200(self):
        response = self.client.post(self.url, self.valid_payload)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn("detail", response.data)
        self.user.refresh_from_db()
        self.assertTrue(self.user.check_password("newsecurepassword"))

    def test_passwords_not_matching_400(self):
        response = self.client.post(
            self.url,
            {
                "new_password": "newsecurepassword",
                "confirm_password": "differentpassword",
            },
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("detail", response.data)

    def test_missing_new_password_400(self):
        response = self.client.post(
            self.url, {"confirm_password": "newsecurepassword"}
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("detail", response.data)

    def test_missing_confirm_password_400(self):
        response = self.client.post(
            self.url, {"new_password": "newsecurepassword"}
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("detail", response.data)

    def test_missing_both_fields_400(self):
        response = self.client.post(self.url, {})
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("detail", response.data)

    def test_invalid_uid_400(self):
        url = reverse(
            "confirm-password",
            kwargs={"uidb64": "invalid!!", "token": self.token},
        )
        response = self.client.post(url, self.valid_payload)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("detail", response.data)

    def test_nonexistent_user_400(self):
        uid = urlsafe_base64_encode(force_bytes(99999))
        url = reverse(
            "confirm-password",
            kwargs={"uidb64": uid, "token": self.token},
        )
        response = self.client.post(url, self.valid_payload)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("detail", response.data)

    def test_invalid_token_400(self):
        url = reverse(
            "confirm-password",
            kwargs={"uidb64": self.uid, "token": "invalidtoken"},
        )
        response = self.client.post(url, self.valid_payload)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("detail", response.data)

    def test_token_invalid_after_password_change(self):
        self.client.post(self.url, self.valid_payload)
        response = self.client.post(self.url, self.valid_payload)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("detail", response.data)
