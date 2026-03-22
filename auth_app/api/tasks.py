from django.core.mail import EmailMultiAlternatives
from django.template.loader import render_to_string

FRONTEND_URL = "http://localhost:8000"


def send_activation_email(email, uid, token, domain):
    activation_link = f"{FRONTEND_URL}/api/activate/{uid}/{token}/"

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
        from_email="noreply@videoflix.de",
        to=[email],
    )
    mail.attach_alternative(html_content, "text/html")
    mail.send()
