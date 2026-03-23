from django.contrib.auth import authenticate
from django.contrib.auth.models import User
from rest_framework import serializers
from rest_framework.exceptions import AuthenticationFailed
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer


class RegistrationSerializer(serializers.ModelSerializer):
    confirmed_password = serializers.CharField(write_only=True)

    class Meta:
        model = User
        fields = [
            "email",
            "password",
            "confirmed_password",
        ]
        extra_kwargs = {
            "password": {"write_only": True, "required": True},
            "email": {"required": True},
        }

    def validate_confirmed_password(self, value):
        password = self.initial_data.get("password")
        if password and value and password != value:
            raise serializers.ValidationError("Passwords do not match.")
        return value

    def validate_email(self, value):
        if User.objects.filter(email=value).exists():
            raise serializers.ValidationError("Email already exists.")
        return value

    def save(self, **kwargs):
        account = User(
            username=self.validated_data["email"],
            email=self.validated_data["email"],
            is_active=False,
        )
        account.set_password(self.validated_data["password"])
        account.save()
        return account


class CustomTokenObtainPairSerializer(TokenObtainPairSerializer):
    """Extend JWT token response with basic user information."""

    username_field = "email"

    def validate(self, attrs: dict) -> dict:
        """Add user details to the token response payload.

        Args:
            attrs: Raw input attributes containing credentials.

        Returns:
            Token data dict extended with user id, username, and email.
        """

        email = attrs.get("email")
        password = attrs.get("password")

        user = authenticate(username=email, password=password)

        if not user:
            raise AuthenticationFailed("Invalid credentials")

        if not user.is_active:
            raise AuthenticationFailed("User inactive")

        self.user = user

        data = super().get_token(user)
        return {
            "refresh": str(data),
            "access": str(data.access_token),
            "user": {
                "id": user.pk,
                "username": user.username,
            },
        }
