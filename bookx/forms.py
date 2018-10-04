from django import forms
from .models import Book

class PostBookForm(forms.ModelForm):
    
    class Meta:
        model = Book
        fields = ('title', 'author', 'cover')