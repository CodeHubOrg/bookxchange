from postman.api import pm_write
from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.conf import settings
from users.email_notifications import send_book_request


def notify_owner_of_request(request, book):
    pm_write(
        sender=request.user,
        recipient=book.owner,
        subject=f"Request to borrow your book {book.title}",
        body=f"{request.user.username} has asked to borrow your book. Please reply to this message, and arrange a time and place where the book can be picked up. Please also send a message if you cannot lend the book.",
        auto_archive=True,
    )
    send_book_request(request, book)


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
