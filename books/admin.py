from django.contrib import admin
from .models import Book


class BookAdmin(admin.ModelAdmin):
    list_display = ("title", "display_author")
    list_filter = ["published_date"]
    search_fields = ["title", "author"]


admin.site.register(Book, BookAdmin)
