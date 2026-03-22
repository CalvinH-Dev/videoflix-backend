from django.contrib.auth.models import User
from django.utils.http import urlsafe_base64_decode
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
