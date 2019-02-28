from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.conf import settings


def notify_owner_of_request(request, book):
    subject = f"Bookx - Request for {book.title}"
    message = render_to_string(
        "emails/loan_request_email.html", {"user": request.user, "book": book}
    )
    to_email = [book.owner.email]
    send_mail(subject, message, settings.DEFAULT_OWNER_EMAIL, to_email)


def notify_of_loan_or_return(request, book, holder, action="Loan"):
    subject = f"Bookx - Confirmation of Book {action}"
    message = render_to_string(
        "emails/loan_or_return_confirmation.html",
        {"type": type, "book": book, "holder": holder},
    )
    to_email = [book.owner.email, holder.email]
    send_mail(subject, message, settings.DEFAULT_OWNER_EMAIL, to_email)


def notify_borrower_of_queue(request, book, holder):
    subject = f"Bookx: Somebody else is interested in {book.title}"
    message = render_to_string(
        "emails/register_interest.html",
        {"user": request.user, "book": book, "holder": holder},
    )
    to_email = [holder.email]
    send_mail(subject, message, settings.DEFAULT_OWNER_EMAIL, to_email)
