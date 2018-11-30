from django.http import HttpResponse, HttpResponseRedirect
from django.views.generic import TemplateView
from django.views.generic.edit import DeleteView, UpdateView
from django.contrib.auth import login, authenticate
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import UserCreationForm
from django.shortcuts import render, redirect
from django.utils import timezone
from django.utils.decorators import method_decorator
from .models import Book
from .forms import PostBookForm


class HomePageView(TemplateView):
    template_name = "home.html"


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


class BookDelete(TemplateView):
    pass


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
        return render(request, self.template_name, {"book": book})
