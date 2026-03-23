from django.urls import path

from auth_app.api.views import (
    ActivateAccountView,
    CookieTokenRefreshView,
    LoginView,
    LogoutView,
    PasswordConfirmView,
    RegistrationView,
    ResetPasswordView,
)

urlpatterns = [
    path("register/", RegistrationView.as_view(), name="registration"),
    path(
        "activate/<str:uidb64>/<str:token>/",
        ActivateAccountView.as_view(),
        name="activate",
    ),
    path("login/", LoginView.as_view(), name="login"),
    path("logout/", LogoutView.as_view(), name="logout"),
    path(
        "token/refresh/",
        CookieTokenRefreshView.as_view(),
        name="token_refresh",
    ),
    path(
        "password_reset/", ResetPasswordView.as_view(), name="reset-password"
    ),
]
