from django.views.generic import TemplateView
from django.shortcuts import render
from books.models import Book


class HomePageView(TemplateView):
    template_name = "home.html"

    def get(self, request):
        return render(request, self.template_name, {"books": Book})
