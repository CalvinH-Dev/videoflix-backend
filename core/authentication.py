from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework_simplejwt.exceptions import InvalidToken, TokenError


class CookieJWTAuthentication(JWTAuthentication):
    """
    Custom JWT authentication class that retrieves
    the access token from cookies.
    """

    def authenticate(self, request):
        """
        Authenticate the user using the JWT access token stored in cookies.

        Args:
            request: Incoming HTTP request.

        Returns:
            Tuple of (user, validated_token) if authentication succeeds, or
            None if no valid token is found.
        """
        access_token = request.COOKIES.get("access_token")

        if not access_token:
            return None

        try:
            validated_token = self.get_validated_token(access_token)
            return self.get_user(validated_token), validated_token
        except (InvalidToken, TokenError):
            return None
