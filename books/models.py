from django.db import models
from django.urls import reverse
from django.contrib.auth import get_user_model

CustomUser = get_user_model()
superuser_id = CustomUser.objects.filter(is_superuser=True)[0].id

class Book(models.Model):
    title = models.CharField(max_length=100)
    author = models.CharField(max_length=100)
    cover = models.ImageField(upload_to='covers/', blank=True)
    published_date = models.DateTimeField(blank=True, null=True)
    last_updated = models.DateTimeField(auto_now_add=True, null=True)
    owner = models.ForeignKey(get_user_model(), on_delete=models.PROTECT, default=superuser_id)

    @property
    def display_author(self):
        name = self.author.split(' ')
        if len(name) > 1:
            name[-1] = name[-1]+", "
        lastfirst = name[-1:] + name[:-1]
        return "".join(lastfirst)

    def get_absolute_url(self):
        return reverse('book_detail', kwargs={'pk':self.pk})
    
    @property
    def absolute_url(self):
        return self.get_absolute_url()    

    @property
    def update_url(self):
        return reverse('book_update', kwargs={'pk':self.pk})
    
    @property
    def delete_url(self):
        return reverse('book_delete', kwargs={'pk':self.pk})

    def __str__(self):
        return self.title
