from django.contrib.auth import get_user_model
from django.contrib.auth.models import User
from django.contrib.auth.tokens import default_token_generator
from django.utils.encoding import force_bytes
from django.utils.http import urlsafe_base64_decode, urlsafe_base64_encode
from rest_framework import status
from rest_framework.response import Response
from rest_framework.utils.serializer_helpers import force_str

from auth_app.models import ActivationToken


def decode_uid(uidb64: str) -> bytes | str | None:
    try:
        return force_str(urlsafe_base64_decode(uidb64))
    except Exception:
        return None


def get_user(uid: str | bytes) -> User | None:
    return User.objects.filter(pk=uid).first()


def get_activation(user: User, token: str) -> ActivationToken | None:
    return ActivationToken.objects.filter(user=user, token=token).first()


def create_token_and_uid_for_user(user):
    token = default_token_generator.make_token(user)
    uid = urlsafe_base64_encode(force_bytes(user.pk))
    return token, uid


def get_passwords(data: dict) -> tuple[str | None, str | None]:
    return data.get("new_password"), data.get("confirm_password")


def validate_passwords(new_password: str | None, confirm_password: str | None):
    if not new_password or not confirm_password:
        return Response(
            {"detail": "Bitte beide Felder ausfüllen."},
            status=status.HTTP_400_BAD_REQUEST,
        )

    if new_password != confirm_password:
        return Response(
            {"detail": "Passwörter stimmen nicht überein."},
            status=status.HTTP_400_BAD_REQUEST,
        )

    return None


def get_user_from_uid(uidb64: str):
    try:
        uid = urlsafe_base64_decode(uidb64).decode()
    except (ValueError, OverflowError):
        return None

    return User.objects.filter(pk=uid).first()


def validate_token(user, token: str):
    if not user:
        return Response(
            {"detail": "Ungültiger Link."},
            status=status.HTTP_400_BAD_REQUEST,
        )

    if not default_token_generator.check_token(user, token):
        return Response(
            {"detail": "Token ungültig oder abgelaufen."},
            status=status.HTTP_400_BAD_REQUEST,
        )

    return None
