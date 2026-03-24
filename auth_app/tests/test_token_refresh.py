from django.contrib.auth import get_user_model
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase
from rest_framework_simplejwt.tokens import RefreshToken

User = get_user_model()


class TokenRefreshViewTest(APITestCase):
    def setUp(self):
        self.url = reverse("token_refresh")

        self.user = User.objects.create(
            email="user@example.com",
            username="user@example.com",
            is_active=True,
        )
        self.user.set_password("securepassword")
        self.user.save()

        self.refresh = RefreshToken.for_user(self.user)
        self.refresh_token = str(self.refresh)

    def test_token_refresh_200(self):
        self.client.cookies["refresh_token"] = self.refresh_token

        response = self.client.post(self.url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn("detail", response.data)

    def test_token_refresh_sets_access_cookie(self):
        self.client.cookies["refresh_token"] = self.refresh_token

        response = self.client.post(self.url)

        self.assertIn("access_token", response.cookies)
        self.assertNotEqual(response.cookies["access_token"].value, "")

    def test_token_refresh_without_cookie_400(self):
        response = self.client.post(self.url)

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("detail", response.data)

    def test_token_refresh_invalid_token_401(self):
        self.client.cookies["refresh_token"] = "invalid_token"

        response = self.client.post(self.url)

        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        self.assertIn("detail", response.data)

    def test_token_refresh_blacklisted_token_401(self):
        self.refresh.blacklist()
        self.client.cookies["refresh_token"] = self.refresh_token

        response = self.client.post(self.url)

        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
