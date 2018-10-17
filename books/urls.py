from django.urls import path

from books import views

urlpatterns = [
    path('', views.HomePageView.as_view(), name='home'),
    path('books/', views.BookListView.as_view(), name='book_list'),
    path('book/new', views.BookNewView.as_view(), name='book_new'),
    path('book/<int:pk>', views.BookDetailView.as_view(), name="book_detail"),
]

