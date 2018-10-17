from django.db import models
from django.urls import reverse

class Book(models.Model):
    title = models.CharField(max_length=100)
    author = models.CharField(max_length=100)
    cover = models.ImageField(upload_to='covers/')
    published_date = models.DateTimeField(blank=True, null=True)
    # last_updated = models.DateTimeField(auto_now_add=True)
    # owner = models.ForeignKey(User, related_name='books')

    @property
    def display_author(self):
        name = self.author.split(' ')
        if len(name) > 1:
            name[-1] = name[-1]+", "
        lastfirst = name[-1:] + name[:-1]
        return "".join(lastfirst)

    @property
    def absolute_url(self):
        return reverse('book_detail', kwargs={'pk':self.pk})
    

    def __str__(self):
        return self.title
