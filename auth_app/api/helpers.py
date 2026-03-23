from django.contrib.auth.models import User
from django.contrib.auth.tokens import default_token_generator
from django.utils.encoding import force_bytes
from django.utils.http import urlsafe_base64_decode, urlsafe_base64_encode
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
