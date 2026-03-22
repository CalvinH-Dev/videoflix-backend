from django.contrib.auth.models import User
from django.utils.http import urlsafe_base64_decode
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.utils.serializer_helpers import force_str
from rest_framework.views import APIView, status

from auth_app.api.helpers import decode_uid, get_activation, get_user
from auth_app.api.serializers import RegistrationSerializer
from auth_app.models import ActivationToken


class RegistrationView(APIView):
    """Handle user registration."""

    permission_classes = [AllowAny]

    def get(self, request):
        return Response({"text": "hello"}, status=status.HTTP_200_OK)

    def post(self, request):
        serializer = RegistrationSerializer(data=request.data)

        if not serializer.is_valid():
            return Response(
                serializer.errors, status=status.HTTP_400_BAD_REQUEST
            )

        serializer.save()

        return Response(
            {"message": "Bitte bestätige deine E-Mail"},
            status=status.HTTP_201_CREATED,
        )


class ActivateAccountView(APIView):
    permission_classes = [AllowAny]

    def get(self, request, uidb64, token):
        uid = decode_uid(uidb64)
        if not uid:
            return Response({"detail": "Ungültiger Link."}, status=400)

        user = get_user(uid)
        if not user:
            return Response({"detail": "Ungültiger Link."}, status=400)

        activation = get_activation(user, token)
        if not activation:
            return Response(
                {"detail": "Token ungültig oder bereits verwendet."},
                status=400,
            )

        if activation.is_expired():
            activation.delete()
            return Response({"detail": "Token abgelaufen."}, status=400)

        user.is_active = True
        user.save()
        activation.delete()
        return Response({"detail": "Account aktiviert."})
