from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render, redirect
from django.shortcuts import render, redirect
from django.utils import timezone
from .models import Book
from .forms import PostBookForm



def index(request):
    return render(request, 'bookx/base.html', {})

def book_list(request): 
    books = Book.objects.filter(published_date__lte=timezone.now()).order_by('published_date')
    return render(request, 'bookx/book_list.html', {'books': books})

def book_new(request):
    if request.method == 'POST':
        form = PostBookForm(request.POST, request.FILES)
        if form.is_valid():
            book = form.save(commit=False)
            book.published_date = timezone.now()
            book.save()
            return redirect('book_list')                    
    else: 
        form = PostBookForm()
    return render(request, 'bookx/book_edit.html', {'form': form})
