from django.db import models
from django.conf import settings


class Book(models.Model):
    title = models.CharField(max_length=100)
    author = models.CharField(max_length=100)
    cover = models.ImageField(upload_to='covers/')
    published_date = models.DateTimeField(blank=True, null=True)
    last_updated = models.DateTimeField(auto_now_add=True)
    owner = models.ForeignKey(User, related_name='books')

    def __str__(self):
        return self.title

