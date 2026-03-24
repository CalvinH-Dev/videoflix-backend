from django.conf import settings
from django.contrib.auth.models import User
from jwt.exceptions import DecodeError
from rest_framework.generics import CreateAPIView
from rest_framework.permissions import AllowAny
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.views import APIView, status
from rest_framework_simplejwt.exceptions import TokenBackendError, TokenError
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
)

from auth_app.api.helpers import (
    create_token_and_uid_for_user,
    decode_uid,
    get_activation,
    get_passwords,
    get_user,
    get_user_from_uid,
    validate_passwords,
    validate_token,
)
from auth_app.api.serializers import (
    CustomTokenObtainPairSerializer,
    RegistrationSerializer,
)
from auth_app.api.tasks import send_password_reset_email
from core.redis_client import get_queue


class RegistrationView(CreateAPIView):
    """
    Handle user registration.

    Attributes:
        serializer_class: Serializer used for user registration.
        permission_classes: Permissions required for this view.
    """

    serializer_class = RegistrationSerializer
    permission_classes = [AllowAny]

    def create(self, request, *args, **kwargs) -> Response:
        """
        Create a new user account.

        Args:
            request: Incoming request containing user registration data.

        Returns:
            Response with success message and HTTP 201 status.
        """
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()

        return Response(
            {"message": "Bitte bestätige deine E-Mail"},
            status=status.HTTP_201_CREATED,
        )


class ActivateAccountView(APIView):
    """
    Handle account activation via token link.

    Attributes:
        permission_classes: Permissions required for this view.
    """

    permission_classes = [AllowAny]

    def get(self, request, uidb64: str, token: str) -> Response:
        """
        Activate a user's account using a UID and token.

        Args:
            request: Incoming request.
            uidb64: Base64-encoded user ID.
            token: Activation token.

        Returns:
            Response with success or error message depending on token validity.
        """
        uid = decode_uid(uidb64)
        if not uid:
            return Response({"detail": "Invalid link."}, status=400)

        user = get_user(uid)
        if not user:
            return Response({"detail": "Invalid link."}, status=400)

        activation = get_activation(user, token)
        if not activation:
            return Response(
                {"detail": "Token invalid or already used."},
                status=400,
            )

        if activation.is_expired():
            activation.delete()
            return Response({"detail": "Token expired."}, status=400)

        user.is_active = True
        user.save()
        activation.delete()
        return Response({"detail": "Account activated."})


class LoginView(TokenObtainPairView):
    """
    Handle user login and set JWT tokens as HTTP-only cookies.

    Attributes:
        serializer_class: Serializer used for login.
        permission_classes: Permissions required for this view.
    """

    permission_classes = [AllowAny]
    serializer_class = CustomTokenObtainPairSerializer

    def post(self, request: Request, *args, **kwargs) -> Response:
        """
        Authenticate user and set access/refresh token cookies.

        Args:
            request: Incoming request containing login credentials.

        Returns:
            Response with login success message, user info, and tokens as cookies.
        """
        response = super().post(request, *args, **kwargs)
        refresh_token = response.data.get("refresh")
        access_token = response.data.get("access")
        user = response.data.get("user")

        response.set_cookie(
            key="access_token",
            value=access_token,
            httponly=True,
            secure=settings.COOKIE_SECURE,
            samesite="Lax",
        )
        response.set_cookie(
            key="refresh_token",
            value=refresh_token,
            httponly=True,
            secure=settings.COOKIE_SECURE,
            samesite="Lax",
        )
        response.data = {"detail": "Login successful", "user": user}
        return response


class LogoutView(APIView):
    """
    Handle user logout by blacklisting refresh token and clearing cookies.

    Attributes:
        permission_classes: Permissions required for this view.
    """

    permission_classes = [AllowAny]

    def post(self, request: Request, *args, **kwargs) -> Response:
        """
        Logout user by blacklisting the refresh token and deleting cookies.

        Args:
            request: Incoming request containing the refresh token.

        Returns:
            Response with success or error message.
        """
        refresh_token = request.COOKIES.get("refresh_token")
        if not refresh_token:
            return Response(
                {"detail": "Refresh token not found."},
                status=status.HTTP_400_BAD_REQUEST,
            )
        try:
            token = RefreshToken(refresh_token)
            token.blacklist()
        except (TokenError, TokenBackendError, DecodeError):
            return Response(
                {"detail": "Invalid or expired token."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        response = Response(
            {"detail": "Logout successful. Refresh token invalidated."},
            status=status.HTTP_200_OK,
        )
        response.delete_cookie("access_token")
        response.delete_cookie("refresh_token")
        return response


class CookieTokenRefreshView(TokenRefreshView):
    """
    Refresh the access token using the refresh token stored in cookies.

    Attributes:
        permission_classes: Permissions required for this view.
    """

    permission_classes = [AllowAny]

    def post(self, request: Request, *args, **kwargs) -> Response:
        """
        Issue a new access token from a valid refresh token cookie.

        Args:
            request: Incoming request containing the refresh token cookie.

        Returns:
            Response with new access token or error if token invalid.
        """
        refresh_token = request.COOKIES.get("refresh_token")
        if not refresh_token:
            return Response(
                {"detail": "Refresh token not found"},
                status=status.HTTP_400_BAD_REQUEST,
            )
        try:
            serializer = self.get_serializer(data={"refresh": refresh_token})
            serializer.is_valid(raise_exception=True)
        except (TokenError, TokenBackendError, Exception):
            return Response(
                {"detail": "Invalid or expired token."},
                status=status.HTTP_401_UNAUTHORIZED,
            )

        access_token = serializer.validated_data.get("access")
        response = Response({"detail": "Token refreshed"})
        response.set_cookie(
            key="access_token",
            value=access_token,
            httponly=True,
            secure=settings.COOKIE_SECURE,
            samesite="Lax",
        )
        return response


class ResetPasswordView(APIView):
    """
    Handle password reset requests by sending reset emails.

    Attributes:
        permission_classes: Permissions required for this view.
    """

    permission_classes = [AllowAny]

    def post(self, request: Request, *args, **kwargs) -> Response:
        """
        Initiate password reset process by sending an email with token link.

        Args:
            request: Incoming request containing user's email.

        Returns:
            Response with success message regardless of whether the user exists.
        """
        email = request.data.get("email")

        if not email:
            return Response(
                {"detail": "Email is missing."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        response = {
            "detail": "If an account exists, a password reset email has been sent."
        }

        user = User.objects.filter(email=email).first()
        if not user:
            return Response(response, status=status.HTTP_200_OK)

        token, uid = create_token_and_uid_for_user(user)
        q = get_queue("high")
        q.enqueue(send_password_reset_email, email, uid, token)

        return Response(response, status=status.HTTP_200_OK)


class PasswordConfirmView(APIView):
    """
    Confirm new password using UID and token, and update user's password.

    Attributes:
        permission_classes: Permissions required for this view.
    """

    permission_classes = [AllowAny]

    def post(
        self, request: Request, uidb64: str, token: str, *args, **kwargs
    ) -> Response:
        """
        Set a new password for the user after validating token and password match.

        Args:
            request: Incoming request containing new password data.
            uidb64: Base64-encoded user ID.
            token: Password reset token.

        Returns:
            Response with success or error message.
        """
        new_password, confirm_password = get_passwords(request.data)

        error = validate_passwords(new_password, confirm_password)
        if error:
            return error

        user = get_user_from_uid(uidb64)

        error = validate_token(user, token)
        if error:
            return error

        user.set_password(new_password)
        user.save()

        return Response(
            {"detail": "Password successfully changed."},
            status=status.HTTP_200_OK,
        )
