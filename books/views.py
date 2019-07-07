from django.urls import reverse_lazy
from django.http import HttpResponseRedirect
from django.core.exceptions import ImproperlyConfigured
from django.views.generic import TemplateView, DetailView
from django.views.generic.edit import DeleteView, UpdateView
from django.contrib.auth.decorators import login_required
from django.shortcuts import render
from django.utils import timezone
from django.utils.decorators import method_decorator

from bookx.context_processors import books_action
from .models import Book, BookHolder, Category
from .forms import PostBookForm  # , RequestBookForm
from .notifications import (
    notify_owner_of_request,
    notify_of_loan_or_return,
    notify_borrower_of_queue,
)


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
        categories = Category.objects.all()
        books = Book.objects.filter(published_date__lte=timezone.now()).exclude(status="NA")
        return render(
            request,
            self.template_name,
            {"categories": categories, "books": books},
        )


class BookCategoryView(BookListView):
    template_name = "books/book_list.html"

    def get_query_param(self, request):
        url_parts = request.path.split("/")
        return url_parts[3].capitalize()

    def get(self, request, category):
        categories = Category.objects.all()
        books = Book.objects.get_books_in_category(category.capitalize()).exclude(status="NA")
        query_param = self.get_query_param(request)
        return render(
            request,
            self.template_name,
            {"categories": categories, "books": books, "cat": query_param},
        )


class BookSuperCategoryView(BookCategoryView):
    template_name = "books/book_list.html"

    def get(self, request, supercategory):
        categories = Category.objects.all()
        books = Book.objects.get_books_in_supercategory(
            supercategory.capitalize()
        ).exclude(status="NA")
        query_param = self.get_query_param(request)
        return render(
            request,
            self.template_name,
            {
                "categories": categories,
                "books": books,
                "supercat": query_param,
            },
        )


class BookDetailView(TemplateView):
    template_name = "books/book_detail.html"

    def get(self, request, pk):

        return render(request, self.template_name)


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

    def create_book_holder(self, book, holder, status):
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
            notify_owner_of_request(self.request, book)

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
        notify_of_loan_or_return(self.request, book, holder)


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
        notify_of_loan_or_return(self.request, book, holder, type="Return")


class BookInterest(BaseLoanView):
    model = Book
    success_url = "email_success"
    template_name_suffix = "_confirm_interest_item"
    new_status = "OL"

    def create_book_holder(self, book, holder, status):
        notify_borrower_of_queue(self.request, book, holder)


class Success(TemplateView):
    template_name = "success.html"


class BookChangeStatus(TemplateView):
    template_name = "books/book_change_status.html"

    def get(self, request, *args, **kwargs):
        return render(request, self.template_name, books_action(request))

    def post(self, request, *args, **kwargs):
        book_id = kwargs["pk"]
        book = Book.objects.get(id=book_id)
        action = kwargs["action"]
        if action == "withdraw":
            book.status = "NA"
        elif action == "set_available":
            book.status = "AV"
        book.save()
        return HttpResponseRedirect(
            reverse_lazy("book_detail", kwargs={"pk": book_id})
        )
