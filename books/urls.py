from django.urls import path
from django.contrib.auth.decorators import login_required

from books import views

urlpatterns = [
    path("", views.BookListView.as_view(), name="book_list"),
    path(
        "category/<str:category>/",
        views.BookCategoryView.as_view(),
        name="book_category",
    ),
    path("new", login_required(views.BookNewView.as_view()), name="book_new"),
    path(
        "<int:pk>/update",
        login_required(views.BookUpdate.as_view()),
        name="book_update",
    ),
    path(
        "<int:pk>/request_item/",
        login_required(views.BookRequest.as_view()),
        name="book_request_item",
    ),
    path(
        "<int:pk>/lend_item/",
        login_required(views.BookLend.as_view()),
        name="book_lend_item",
    ),
    path(
        "<int:pk>/return_item/",
        login_required(views.BookReturn.as_view()),
        name="book_return_item",
    ),
    path(
        "<int:pk>/delete",
        login_required(views.BookDelete.as_view()),
        name="book_delete",
    ),
    path(
        "<int:pk>/interest",
        login_required(views.BookInterest.as_view()),
        name="book_interest",
    ),
    path("<int:pk>/success", views.Success.as_view(), name="email_success"),
    path("<int:pk>/", views.BookDetailView.as_view(), name="book_detail"),
]
