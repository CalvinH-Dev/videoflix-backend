from django.conf import settings
from django.core.mail import EmailMultiAlternatives
from django.template.loader import render_to_string


def send_activation_email(email, uid, token):
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
        subject="Aktiviere deinen Videoflix Account",
        body=f"Aktiviere deinen Account: {activation_link}",
        from_email=settings.DEFAULT_FROM_EMAIL,
        to=[email],
    )
    mail.attach_alternative(html_content, "text/html")
    mail.send()


def send_password_reset_email(email, uid, token):
    reset_link = f"{settings.FRONTEND_URL.rstrip('/')}/pages/auth/confirm_password.html?uid={uid}&token={token}"

    html_content = render_to_string(
        "emails/password_reset.html",
        context={
            "reset_link": reset_link,
            "email": email,
        },
    )

    mail = EmailMultiAlternatives(
        subject="Setze dein Videoflix Passwort zurück",
        body=f"Setze dein Passwort zurück deinen Account: {reset_link}",
        from_email=settings.DEFAULT_FROM_EMAIL,
        to=[email],
    )
    mail.attach_alternative(html_content, "text/html")
    mail.send()
