from django.contrib import admin
from .models import Book

class BookAdmin(admin.ModelAdmin):
    list_display = ('title', 'display_author')
    list_filter = ['published_date']
    search_fields = ['title','author']

    def display_author(self, obj):
        name = obj.author.split(' ')
        if len(name) > 1:
            name[-1] = name[-1]+", "
        lastfirst = name[-1:] + name[:-1]
        return "".join(lastfirst)

admin.site.register(Book, BookAdmin)
