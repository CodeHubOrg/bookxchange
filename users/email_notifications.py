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


def send_book_request(request, book):
    subject = f"Somebody would like to borrow {book.title}"
    user = request.user
    owner = book.owner
    token = account_activation_token.make_token(owner)
    uid = urlsafe_base64_encode(force_bytes(owner.pk))
    to_email = [owner.email]
    message = render_to_string(
        "emails/book_request_email.html",
        {
            "user": user,
            "owner": owner,
            "book": book,
            "loginurl": request.build_absolute_uri(
                reverse("emaillogin", kwargs=dict(uidb64=uid, token=token))
            ),
        },
    )
    send_mail(subject, message, settings.DEFAULT_OWNER_EMAIL, to_email)


def send_reply_notification(msg, user, site):
    subject = msg.subject
    body = msg.body
    token = account_activation_token.make_token(user)
    uid = urlsafe_base64_encode(force_bytes(user.id))
    to_email = [user.email]
    login_path = reverse("emaillogin", kwargs=dict(uidb64=uid, token=token))
    login_url = f"https://{site}{login_path}"
    message = render_to_string(
        "emails/reply_email.html",
        {
            "user": user,
            "body": body,
            "loginurl": login_url
        }
    )
    send_mail(subject, message, settings.DEFAULT_OWNER_EMAIL, to_email)
