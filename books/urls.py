from django.urls import path
from django.contrib.auth.decorators import login_required

from books import views

urlpatterns = [
    path("", views.BookListView.as_view(), name="book_list"),
    path("new", login_required(views.BookNewView.as_view()), name="book_new"),
    path(
        "<int:pk>/update",
        login_required(views.BookUpdate.as_view()),
        name="book_update",
    ),
    path(
        "<int:pk>/delete",
        login_required(views.BookDelete.as_view()),
        name="book_delete",
    ),
    path("<int:pk>", views.BookDetailView.as_view(), name="book_detail"),
]
