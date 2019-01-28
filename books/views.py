from django.urls import reverse_lazy
from django.http import HttpResponse, HttpResponseRedirect
from django.core.mail import send_mail, BadHeaderError
from django.core.exceptions import ImproperlyConfigured
from django.views.generic import TemplateView, DetailView
from django.views.generic.edit import DeleteView, UpdateView
from django.contrib.auth.decorators import login_required
from django.shortcuts import render
from django.utils import timezone
from django.utils.decorators import method_decorator

from .models import Book, BookHolder
from .forms import PostBookForm  # , RequestBookForm


class BookNewView(TemplateView):
    form_class = PostBookForm
    template_name = "books/book_edit.html"

    def get(self, request):
        form = self.form_class()
        return render(request, self.template_name, {"form": form})

    def post(self, request):
        form = self.form_class(request.POST, request.FILES)
        if form.is_valid():
            book = form.save(commit=False)
            book.published_date = timezone.now()
            if request.user.is_authenticated:
                book.owner = request.user
            book.save()
            return HttpResponseRedirect("/books")
        return render(request, self.template_name, {"form": form})

    @method_decorator(login_required, name="dispatch")
    def dispatch(self, request):
        return super(BookNewView, self).dispatch(request)


class BookUpdate(UpdateView):
    model = Book
    form_class = PostBookForm
    template_name = "books/book_edit.html"


class BookDelete(DeleteView):
    model = Book
    success_url = reverse_lazy("book_list")


class BookListView(TemplateView):
    template_name = "books/book_list.html"

    def get(self, request):
        books = Book.objects.filter(
            published_date__lte=timezone.now()
        ).order_by("published_date")
        return render(request, self.template_name, {"books": books})


class BookDetailView(TemplateView):
    template_name = "books/book_detail.html"

    def get(self, request, pk):
        book = Book.objects.get(pk=pk)
        holder = book.get_holder_for_current_status()
        date = None
        if holder:
            date = book.get_date_for_status(book.status)
        return render(
            request,
            self.template_name,
            {"book": book, "holder": holder, "date": date},
        )


class BaseLoanView(DetailView):
    """
    Base view for changing loan status on an object.

    Using this base class requires subclassing to provide a response mixin.
    """

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
        holder = self.get_new_holder(request, *args, **kwargs)
        success_url = self.get_success_url(book.id)
        new_status = self.get_new_status()
        self.new_status = new_status
        self.create_book_holder(book, holder, new_status)

        return HttpResponseRedirect(success_url)

    def create_book_holder(self, book, holder, status):
        # do try and error here
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

    def get_current_holder(self, request, *args, **kwargs):
        book = self.object
        holder = book.get_holder_for_current_status()
        # for this not using try except because None is a valid
        # value; if it's a new book there is no 'holder'
        return holder

    def get_new_holder(self, request, *args, **kwargs):
        return self.get_current_holder(request, *args, **kwargs)

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

    def get_new_status(self):
        if self.new_status:
            return self.new_status.format(**self.object.__dict__)
        else:
            raise ImproperlyConfigured("No proper status for book lending.")

    def get(self, request, *args, **kwargs):
        self.object = self.get_object()
        holder = self.get_current_holder(request, *args, **kwargs)
        context = self.get_context_data(object=self.object, holder=holder)
        return self.render_to_response(context)

    # Add support for browsers which only accept GET and POST for now.
    def post(self, request, *args, **kwargs):
        return self.loan_item(request, *args, **kwargs)


class BookRequest(BaseLoanView):
    model = Book
    new_status = "RQ"
    allowed_status = ["AV"]
    template_name_suffix = "_confirm_request_item"
    success_url = "book_detail"

    def get_new_holder(self, request, *args, **kwargs):
        return request.user


class BookLend(BaseLoanView):
    model = Book
    new_status = "OL"
    template_name_suffix = "_confirm_loan_item"
    success_url = "book_detail"

    def create_book_holder(self, book, holder, status):
        book.status = status
        BookHolder.objects.create(
            book=book,
            holder=holder,
            date_borrowed=timezone.now(),
            status=status,
        )
        book.save()


class BookReturn(BaseLoanView):
    model = Book
    new_status = "AV"
    template_name_suffix = "_confirm_return_item"
    success_url = "book_detail"

    def create_book_holder(self, book, holder, status):
        book.status = status
        BookHolder.objects.create(
            book=book,
            holder=holder,
            date_returned=timezone.now(),
            status=status,
        )
        book.save()


class BookInterest(BaseLoanView):
    model = Book
    success_url = "email_success"
    template_name_suffix = "_confirm_interest_item"
    new_status = "OL"

    # def get_new_holder(self, request, *args, **kwargs):
    #     return request.user

    def create_book_holder(self, book, holder, status):
        # add entry in Holder table?
        # probably better to create some other log
        current_user = self.request.user
        from_email = current_user.email
        to_email = [holder.email]
        subject = "Bookx: " + current_user.username + " and " + book.title
        message = (
            "Our records show that you have borrowed the book "
            + book.title
            + ". "
            + current_user.username
            + " is interested in this book. Please could you let them know "
            + "when you will return the book."
        )
        try:
            send_mail(subject, message, from_email, to_email)
        except BadHeaderError:
            return HttpResponse("Invalid header found.")


class Success(TemplateView):
    template_name = "success.html"
