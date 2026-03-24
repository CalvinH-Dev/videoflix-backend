from django.contrib.auth import authenticate
from django.contrib.auth.models import User
from rest_framework import serializers
from rest_framework.exceptions import AuthenticationFailed
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer


class RegistrationSerializer(serializers.ModelSerializer):
    """
    Serializer for user registration.

    Fields:
        email: User's email address.
        password: User's password.
        confirmed_password: Password confirmation for validation.
    """

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

    def validate_confirmed_password(self, value: str) -> str:
        """
        Validate that confirmed_password matches password.

        Args:
            value: Confirmed password input.

        Returns:
            The confirmed password if valid.

        Raises:
            serializers.ValidationError: If passwords do not match.
        """
        password = self.initial_data.get("password")
        if password and value and password != value:
            raise serializers.ValidationError("Passwords do not match.")
        return value

    def validate_email(self, value: str) -> str:
        """
        Validate that the email is not already registered.

        Args:
            value: Email input.

        Returns:
            Email if valid.

        Raises:
            serializers.ValidationError: If email already exists.
        """
        if User.objects.filter(email=value).exists():
            raise serializers.ValidationError("Email already exists.")
        return value

    def save(self, **kwargs) -> User:
        """
        Create and save a new user account.

        Returns:
            Newly created User instance.
        """
        account = User(
            username=self.validated_data["email"],
            email=self.validated_data["email"],
            is_active=False,
        )
        account.set_password(self.validated_data["password"])
        account.save()
        return account


class CustomTokenObtainPairSerializer(TokenObtainPairSerializer):
    """
    Extend JWT token response with basic user information.

    Attributes:
        username_field: Field used for authentication.
    """

    username_field = "email"

    def validate(self, attrs: dict) -> dict:
        """
        Add user details to the token response payload.

        Args:
            attrs: Input attributes containing login credentials.

        Returns:
            Token data dictionary extended with user ID and username.

        Raises:
            AuthenticationFailed: If credentials are invalid or user inactive.
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
