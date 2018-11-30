from django.urls import path
from django.contrib.auth.decorators import login_required

from books import views

urlpatterns = [
    path("", views.HomePageView.as_view(), name="home"),
    path("books/", views.BookListView.as_view(), name="book_list"),
    path("book/new", login_required(views.BookNewView.as_view()), name="book_new"),
    path(
        "book/<int:pk>/update",
        login_required(views.BookUpdate.as_view()),
        name="book_update",
    ),
    path(
        "book/<int:pk>/delete",
        login_required(views.BookDelete.as_view()),
        name="book_delete",
    ),
    path("book/<int:pk>", views.BookDetailView.as_view(), name="book_detail"),
]
