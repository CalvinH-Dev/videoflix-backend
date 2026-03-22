from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.views import APIView, status

from auth_app.api.serializers import RegistrationSerializer


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
