from django.conf import settings
from django.core.mail import EmailMultiAlternatives
from django.template.loader import render_to_string


def send_activation_email(email: str, uid: str, token: str):
    """
    Send an account activation email to the user.

    Args:
        email: Recipient's email address.
        uid: Base64-encoded user ID.
        token: Activation token.
    """
    activation_link = (
        f"{settings.EMAIL_DOMAIN_URL.rstrip('/')}/api/activate/{uid}/{token}/"
    )

    html_content = render_to_string(
        "emails/activation.html",
        context={
            "activation_link": activation_link,
            "email": email,
        },
    )

    mail = EmailMultiAlternatives(
        subject="Activate your Videoflix Account",
        body=f"Activate your account: {activation_link}",
        from_email=settings.DEFAULT_FROM_EMAIL,
        to=[email],
    )
    mail.attach_alternative(html_content, "text/html")
    mail.send()


def send_password_reset_email(email: str, uid: str, token: str):
    """
    Send a password reset email to the user.

    Args:
        email: Recipient's email address.
        uid: Base64-encoded user ID.
        token: Password reset token.
    """
    reset_link = f"{settings.FRONTEND_URL.rstrip('/')}/pages/auth/confirm_password.html?uid={uid}&token={token}"

    html_content = render_to_string(
        "emails/password_reset.html",
        context={
            "reset_link": reset_link,
            "email": email,
        },
    )

    mail = EmailMultiAlternatives(
        subject="Reset your Videoflix Password",
        body=f"Reset your account password: {reset_link}",
        from_email=settings.DEFAULT_FROM_EMAIL,
        to=[email],
    )
    mail.attach_alternative(html_content, "text/html")
    mail.send()
