from django.urls import path

from auth_app.api.views import ActivateAccountView, RegistrationView

urlpatterns = [
    path("register/", RegistrationView.as_view()),
    path("activate/<str:uidb64>/<str:token>/", ActivateAccountView.as_view()),
]
