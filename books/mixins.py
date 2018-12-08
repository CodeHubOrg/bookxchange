from django.contrib.auth import get_user_model
from django.core.exceptions import ImproperlyConfigured
from django.http import HttpResponseRedirect
from django.views.generic.detail import (
    BaseDetailView,
    SingleObjectTemplateResponseMixin,
)
from django.utils import timezone
from .models import BookHolder

# from .forms import RequestBookForm

# (RequestMixin, BaseRequestView, RequestView)


class RequestMixin:
    """Provide the ability to request a book."""

    success_url = None

    def request_item(self, request, *args, **kwargs):
        """
        Call the request_item() method on the fetched
        object and then redirect to the
        success URL.
        """
        self.object = self.get_object()
        book = self.object
        success_url = self.get_success_url()
        holder_id = kwargs["userid"]
        holder = get_user_model().objects.get(id=holder_id)

        if book.status == "AV":
            BookHolder.objects.create(
                book=book, holder=holder, date_requested=timezone.now()
            )
            book.status = "RQ"
            book.save()

        return HttpResponseRedirect(success_url)

    # Add support for browsers which only accept GET and POST for now.
    def post(self, request, *args, **kwargs):
        return self.request_item(request, *args, **kwargs)

    def get_success_url(self):
        if self.success_url:
            return self.success_url.format(**self.object.__dict__)
        else:
            raise ImproperlyConfigured(
                "No URL to redirect to. Provide a success_url."
            )


class BaseRequestView(RequestMixin, BaseDetailView):
    """
    Base view for requesting an object.

    Using this base class requires subclassing to provide a response mixin.
    """


class RequestView(SingleObjectTemplateResponseMixin, BaseRequestView):
    """
    View for deleting an object retrieved with self.get_object(), with a
    response rendered by a template.
    """

    template_name_suffix = "_confirm_request_item"
