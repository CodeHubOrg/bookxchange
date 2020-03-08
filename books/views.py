from django.urls import reverse_lazy
from django.http import HttpResponseRedirect
from django.core.exceptions import ImproperlyConfigured
from django.views.generic import TemplateView, DetailView, ListView
from django.views.generic.edit import DeleteView, UpdateView
from django.contrib.auth.decorators import login_required
from django.shortcuts import render
from django.utils import timezone
from django.utils.decorators import method_decorator
from django.db.models import Q 

from bookx.context_processors import books_action
from .models import Book, Category, Comment, LoanStatus
from .forms import PostBookForm, PostCommentForm  # , RequestBookForm
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
    form_class = PostCommentForm

    def get(self, request, pk):
        form = self.form_class()
        comments = Comment.objects.filter(comment_book_id=pk)
        # import ipdb
        # ipdb.set_trace()
        return render(request, self.template_name, {"form": form, "bookid": pk, "comments": comments})

    def post(self, request, pk):
        form = self.form_class(request.POST)
        if form.is_valid():
            comment = form.save(commit=False)
            comment.published_date = timezone.now()
            comment.comment_book = Book.objects.get(id=pk)
            if request.user.is_authenticated:
                comment.comment_author = request.user
            comment.save()
            return HttpResponseRedirect(
            reverse_lazy("comment_success", kwargs={"pk": pk})
        )
        return render(request, self.template_name, {"form": form})


class BaseLoanView(DetailView):
    """
    Base view for changing loan status on an object.

    Using this base class requires subclassing to provide a response mixin.
    """
    success_url = None

    def change_book_status(self, request, *args, **kwargs):
        """
        Call the change_book_status() method on the fetched
        object and then redirect to the
        success URL.
        """
        self.object = self.get_object()
        book = self.object
        holder = self.get_new_holder(request, book)
        self.change_status(book, holder)
        success_url = self.get_success_url(book.id)

        return HttpResponseRedirect(success_url)

    def change_status(self, book, holder):
        book.loan_item(holder)
        book.save()

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
    def get_current_holder(self, request, book):
        return book.get_holder_for_current_status()

    def get_new_holder(self, request, book):
        return book.get_holder_for_current_status()

    def get(self, request, *args, **kwargs):
        # import ipdb
        # ipdb.set_trace()
        self.object = self.get_object()
        book = self.object
        holder = self.get_current_holder(request, book)
        context = self.get_context_data(object=self.object, holder=holder)
        return self.render_to_response(context)

    # Add support for browsers which only accept GET and POST for now.
    def post(self, request, *args, **kwargs):
        return self.change_book_status(request, *args, **kwargs)


class BookRequest(BaseLoanView):
    model = Book
    template_name_suffix = "_confirm_request_item"
    success_url = "book_detail"

    def get_new_holder(self, request, book):
        return request.user

    def change_status(self, book, holder):
        book.request_item(holder)
        book.save()
        notify_owner_of_request(self.request, book)



class BookLend(BaseLoanView):
    model = Book
    template_name_suffix = "_confirm_loan_item"
    success_url = "book_detail"

    def change_status(self, book, holder):
        user = self.request.user
        if (user.is_superuser or user == book.owner) and user != holder:
            book.loan_item(holder)
        else: 
            book.confirm_loan_borrower(holder)
        book.save()
        notify_of_loan_or_return(self.request, book, holder)


class BookReturn(BaseLoanView):
    model = Book
    template_name_suffix = "_confirm_return_item"
    success_url = "book_detail"

    def change_status(self, book, holder):
        user = self.request.user
        if user.is_superuser or user == book.owner:
            book.return_item(user)
        else: 
            book.return_by_borrower(holder)
        book.save()
        notify_of_loan_or_return(self.request, book, holder, type="Return")


class BookInterest(BaseLoanView):
    model = Book
    template_name_suffix = "_confirm_interest_item"
    success_url = "email_success"

    def change_status(self, book, holder):
        notify_borrower_of_queue(self.request, book, holder)

class BookEmailSuccess(TemplateView):
    template_name = "books/success.html"


class BookCommentSuccess(TemplateView):
    template_name = "books/success_comment.html"

class BookChangeStatus(TemplateView):
    template_name = "books/book_change_status.html"

    def get(self, request, *args, **kwargs):
        return render(request, self.template_name, books_action(request))

    def post(self, request, *args, **kwargs):
        book_id = kwargs["pk"]
        book = Book.objects.get(id=book_id)
        action = kwargs["action"]
        # refactor to use state machine
        if action == "withdraw":
            book.withdraw(request.user)
        elif action == "set_available":
            book.make_available(request.user)
        book.save()
        return HttpResponseRedirect(
            reverse_lazy("book_detail", kwargs={"pk": book_id})
        )

class BookSearchResultsView(BookListView):
    template_name = "books/book_list.html"

    def get(self, request):
        categories = Category.objects.all()
        query = self.request.GET.get('q')
        books = Book.objects.filter(Q(title__icontains=query) | Q(author__icontains=query)).exclude(status="NA")
        return render(
            request,
            self.template_name,
            {"categories": categories, "books": books, "query": query}
        )
