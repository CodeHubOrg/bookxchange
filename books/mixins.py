from django.urls import reverse_lazy
from django.contrib.auth import get_user_model
from django.core.exceptions import ImproperlyConfigured
from django.http import HttpResponseRedirect
from django.views.generic.detail import (
    BaseDetailView,
    SingleObjectTemplateResponseMixin,
)
from django.utils import timezone
from .models import BookHolder


class LoanMixin:
    """Provide the ability to request a book."""

    success_url = None
    new_status = None
    allowed_status = None

    def loan_item(self, request, *args, **kwargs):
        """
        Call the loan_item() method on the fetched
        object and then redirect to the
        success URL.
        """
        self.object = self.get_object()
        book = self.object
        holder = self.get_holder(request, *args, **kwargs)
        success_url = self.get_success_url(book.id)
        status = self.get_status()
        self.createBookHolder(book, holder, status)

        return HttpResponseRedirect(success_url)

    def createBookHolder(self, book, holder, status):
        if self.allowed_status and book.status not in self.allowed_status:
            return HttpResponseRedirect("/")
        else:
            book.status = status
            BookHolder.objects.create(
                book=book,
                holder=holder,
                date_requested=timezone.now(),
                status=status,
            )
            book.save()

    def get_holder(self, request, *args, **kwargs):
        holder_id = kwargs["userid"]
        return get_user_model().objects.get(id=holder_id)

    def get_success_url(self, bookid):
        if self.success_url:
            if bookid:
                self.success_url = reverse_lazy(
                    self.success_url, kwargs={"pk": bookid}
                )
            return self.success_url.format(**self.object.__dict__)
        else:
            raise ImproperlyConfigured(
                "No URL to redirect to. Provide a success_url."
            )

    def get_status(self):
        if self.new_status:
            return self.new_status.format(**self.object.__dict__)
        else:
            raise ImproperlyConfigured("No proper status for book lending.")


class BaseLoanView(LoanMixin, BaseDetailView):
    """
    Base view for changing loan status on an object.

    Using this base class requires subclassing to provide a response mixin.
    """

    def get(self, request, *args, **kwargs):
        self.object = self.get_object()
        holder = self.get_holder(request, *args, **kwargs)
        context = self.get_context_data(object=self.object, holder=holder)
        return self.render_to_response(context)

    # Add support for browsers which only accept GET and POST for now.
    def post(self, request, *args, **kwargs):
        return self.loan_item(request, *args, **kwargs)


class RequestView(SingleObjectTemplateResponseMixin, BaseLoanView):
    """
    View for requesting a book
    """

    template_name_suffix = "_confirm_request_item"
    success_url = "book_detail"


class LendView(SingleObjectTemplateResponseMixin, BaseLoanView):
    """
    View for lending a book
    """

    template_name_suffix = "_confirm_loan_item"
    success_url = "book_detail"

    def createBookHolder(self, book, holder, status):
        book.status = status
        BookHolder.objects.create(
            book=book,
            holder=holder,
            date_borrowed=timezone.now(),
            status=status,
        )
        book.save()


class ReturnView(SingleObjectTemplateResponseMixin, BaseLoanView):
    """
    View for returning a book
    """

    template_name_suffix = "_confirm_return_item"
    success_url = "book_detail"

    def createBookHolder(self, book, holder, status):
        book.status = status
        BookHolder.objects.create(
            book=book,
            holder=holder,
            date_returned=timezone.now(),
            status=status,
        )
        book.save()
