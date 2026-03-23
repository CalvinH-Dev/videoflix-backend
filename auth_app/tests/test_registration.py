from django.contrib.auth import get_user_model
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase

User = get_user_model()


class RegistrationViewTest(APITestCase):
    def setUp(self):
        self.url = reverse("registration")
        self.valid_payload = {
            "email": "user@example.com",
            "password": "securepassword",
            "confirmed_password": "securepassword",
        }

    def test_registration_201(self):
        response = self.client.post(
            self.url, self.valid_payload, format="json"
        )
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        user = User.objects.get(email=self.valid_payload["email"])
        self.assertFalse(user.is_active)

    def test_post_missing_email_returns_400(self):
        payload = {**self.valid_payload}
        del payload["email"]
        response = self.client.post(self.url, payload, format="json")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("email", response.data)

    def test_post_missing_password_returns_400(self):
        payload = {**self.valid_payload}
        del payload["password"]
        response = self.client.post(self.url, payload, format="json")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("password", response.data)

    def test_post_missing_confirmed_password_returns_400(self):
        payload = {**self.valid_payload}
        del payload["confirmed_password"]
        response = self.client.post(self.url, payload, format="json")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("confirmed_password", response.data)

    def test_post_empty_payload_returns_400(self):
        response = self.client.post(self.url, {}, format="json")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("email", response.data)

    def test_post_invalid_email_returns_400(self):
        payload = {**self.valid_payload, "email": "non-valid-email"}
        response = self.client.post(self.url, payload, format="json")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("email", response.data)

    def test_post_passwords_do_not_match_returns_400(self):
        payload = {
            **self.valid_payload,
            "confirmed_password": "different_password",
        }
        response = self.client.post(self.url, payload, format="json")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_post_duplicate_email_returns_400(self):
        self.client.post(self.url, self.valid_payload, format="json")
        response = self.client.post(
            self.url, self.valid_payload, format="json"
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("email", response.data)
