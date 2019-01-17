from django.contrib import admin
from .models import Book, Category


class BookAdmin(admin.ModelAdmin):
    list_display = ("title", "display_author")
    list_filter = ["published_date"]
    search_fields = ["title", "author"]


class CategoryAdmin(admin.ModelAdmin):
    pass


admin.site.register(Book, BookAdmin)
admin.site.register(Category, CategoryAdmin)
