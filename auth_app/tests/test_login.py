from django.contrib.auth import get_user_model
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase

User = get_user_model()


class LoginViewTest(APITestCase):
    def setUp(self):
        self.url = reverse("login")
        self.password = "securepassword"
        self.user = User.objects.create(
            email="user@example.com",
            username="user@example.com",
            is_active=True,
        )
        self.user.set_password(self.password)
        self.user.save()

        self.valid_payload = {
            "email": "user@example.com",
            "password": self.password,
        }

    def test_login_200(self):
        response = self.client.post(
            self.url, self.valid_payload, format="json"
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn("detail", response.data)
        self.assertIn("user", response.data)
        self.assertEqual(response.data["user"]["username"], self.user.username)

    def test_login_sets_cookies(self):
        response = self.client.post(
            self.url, self.valid_payload, format="json"
        )
        self.assertIn("access_token", response.cookies)
        self.assertIn("refresh_token", response.cookies)

    def test_login_invalid_password_401(self):
        payload = {**self.valid_payload, "password": "wrongpassword"}
        response = self.client.post(self.url, payload, format="json")
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_login_invalid_email_401(self):
        payload = {**self.valid_payload, "email": "wrong@example.com"}
        response = self.client.post(self.url, payload, format="json")
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_login_missing_email_400(self):
        payload = {**self.valid_payload}
        del payload["email"]
        response = self.client.post(self.url, payload, format="json")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_login_missing_password_400(self):
        payload = {**self.valid_payload}
        del payload["password"]
        response = self.client.post(self.url, payload, format="json")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_login_inactive_user_401(self):
        self.user.is_active = False
        self.user.save()
        response = self.client.post(
            self.url, self.valid_payload, format="json"
        )
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
