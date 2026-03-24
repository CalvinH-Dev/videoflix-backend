from django.contrib.auth.models import User
from django.contrib.auth.tokens import default_token_generator
from django.utils.encoding import force_bytes
from django.utils.http import urlsafe_base64_decode, urlsafe_base64_encode
from rest_framework import status
from rest_framework.response import Response
from rest_framework.utils.serializer_helpers import force_str

from auth_app.models import ActivationToken


def decode_uid(uidb64: str) -> bytes | str | None:
    """
    Decode a base64-encoded user ID.

    Args:
        uidb64: Base64-encoded user ID.

    Returns:
        Decoded user ID as string or bytes, or None if decoding fails.
    """
    try:
        return force_str(urlsafe_base64_decode(uidb64))
    except Exception:
        return None


def get_user(uid: str | bytes) -> User | None:
    """
    Retrieve a user instance by primary key.

    Args:
        uid: User ID (string or bytes).

    Returns:
        User instance if found, None otherwise.
    """
    return User.objects.filter(pk=uid).first()


def get_activation(user: User, token: str) -> ActivationToken | None:
    """
    Retrieve an activation token for a user.

    Args:
        user: User instance.
        token: Activation token string.

    Returns:
        ActivationToken instance if found, None otherwise.
    """
    return ActivationToken.objects.filter(user=user, token=token).first()


def create_token_and_uid_for_user(user: User) -> tuple[str, str]:
    """
    Generate a new token and base64-encoded UID for a user.

    Args:
        user: User instance.

    Returns:
        Tuple containing the token string and UID string.
    """
    token = default_token_generator.make_token(user)
    uid = urlsafe_base64_encode(force_bytes(user.pk))
    return token, uid


def get_passwords(data: dict) -> tuple[str | None, str | None]:
    """
    Extract new and confirm password fields from request data.

    Args:
        data: Dictionary containing password fields.

    Returns:
        Tuple of (new_password, confirm_password).
    """
    return data.get("new_password"), data.get("confirm_password")


def validate_passwords(
    new_password: str | None, confirm_password: str | None
) -> Response | None:
    """
    Validate that both passwords are present and match.

    Args:
        new_password: New password input.
        confirm_password: Confirm password input.

    Returns:
        Response with error message if invalid, or None if valid.
    """
    if not new_password or not confirm_password:
        return Response(
            {"detail": "Please fill in both fields."},
            status=status.HTTP_400_BAD_REQUEST,
        )

    if new_password != confirm_password:
        return Response(
            {"detail": "Passwords do not match."},
            status=status.HTTP_400_BAD_REQUEST,
        )

    return None


def get_user_from_uid(uidb64: str) -> User | None:
    """
    Retrieve a user instance from a base64-encoded UID.

    Args:
        uidb64: Base64-encoded user ID.

    Returns:
        User instance if found, None otherwise.
    """
    try:
        uid = urlsafe_base64_decode(uidb64).decode()
    except (ValueError, OverflowError):
        return None

    return User.objects.filter(pk=uid).first()


def validate_token(user: User | None, token: str) -> Response | None:
    """
    Validate a user's token for account activation or password reset.

    Args:
        user: User instance.
        token: Token string.

    Returns:
        Response with error message if token is invalid or expired, or None if valid.
    """
    if not user:
        return Response(
            {"detail": "Invalid link."},
            status=status.HTTP_400_BAD_REQUEST,
        )

    if not default_token_generator.check_token(user, token):
        return Response(
            {"detail": "Token invalid or expired."},
            status=status.HTTP_400_BAD_REQUEST,
        )

    return None
