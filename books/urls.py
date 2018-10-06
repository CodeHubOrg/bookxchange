from django.urls import path

from . import views

urlpatterns = [
    path('', views.HomePageView.as_view(), name='home'),
    path('books/', views.book_list, name='book_list'),
    path('book/new', views.book_new, name='book_new'),
]