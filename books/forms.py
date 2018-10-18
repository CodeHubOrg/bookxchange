from django import forms
from .models import Book

class PostBookForm(forms.ModelForm):
    
    class Meta:
        model = Book
        fields = ('title', 'author', 'cover')

    def clean_author(self): 
        data = self.cleaned_data.get('author')
        if len(data) <= 3:
            raise forms.ValidationError('Author needs to be longer than two characters')
        return data