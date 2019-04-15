from django.urls import reverse
from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.utils.encoding import force_bytes
from users.tokens import account_activation_token
from django.utils.http import urlsafe_base64_encode
from django.conf import settings


def send_account_confirmation(request, user, to_email):
    subject = "Activate your Bookx account."
    token = account_activation_token.make_token(user)
    uid = urlsafe_base64_encode(force_bytes(user.pk))
    message = render_to_string(
        "emails/acc_activate_email.html",
        {
            "user": user,
            "activate_url": request.build_absolute_uri(
                reverse("activate", kwargs=dict(uidb64=uid, token=token))
            ),
        },
    )
    send_mail(subject, message, settings.DEFAULT_OWNER_EMAIL, to_email)
