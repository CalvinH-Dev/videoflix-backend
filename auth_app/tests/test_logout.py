from django.contrib.auth import get_user_model
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase
from rest_framework_simplejwt.tokens import RefreshToken

User = get_user_model()


class LogoutViewTest(APITestCase):
    def setUp(self):
        self.url = reverse("logout")

        self.user = User.objects.create(
            email="user@example.com",
            username="user@example.com",
            is_active=True,
        )
        self.user.set_password("securepassword")
        self.user.save()

        self.refresh = RefreshToken.for_user(self.user)
        self.refresh_token = str(self.refresh)

    def test_logout_200(self):
        self.client.cookies["refresh_token"] = self.refresh_token

        response = self.client.post(self.url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn("detail", response.data)

    def test_logout_deletes_cookies(self):
        self.client.cookies["refresh_token"] = self.refresh_token

        response = self.client.post(self.url)

        self.assertEqual(response.cookies["access_token"].value, "")
        self.assertEqual(response.cookies["refresh_token"].value, "")
        self.assertEqual(response.cookies["access_token"]["max-age"], 0)
        self.assertEqual(response.cookies["refresh_token"]["max-age"], 0)

    def test_logout_without_token_400(self):
        response = self.client.post(self.url)

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data["detail"], "Refresh token not found.")

    def test_logout_invalid_token_400(self):
        self.client.cookies["refresh_token"] = "invalid_token"

        response = self.client.post(self.url)

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data["detail"], "Invalid or expired token.")
