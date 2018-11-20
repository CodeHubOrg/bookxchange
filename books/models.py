from django.db import models
from django.urls import reverse
from django.contrib.auth import get_user_model
from django.conf import settings

from django.core.files.base import ContentFile
from django.core.files.storage import default_storage as storage

from PIL import Image, ImageOps
from io import BytesIO
from django.core.files.uploadedfile import InMemoryUploadedFile
import sys
import os



default_owner_name = "Codehub"
def get_default_owner():
    return get_user_model().objects.get_or_create(username=default_owner_name)

class Book(models.Model):
    title = models.CharField(max_length=100)
    author = models.CharField(max_length=100)
    cover = models.ImageField(upload_to='covers/', blank=True)
    thumb = models.ImageField(upload_to='covers/', blank=True)
    published_date = models.DateTimeField(blank=True, null=True)
    last_updated = models.DateTimeField(auto_now_add=True, null=True)
    owner = models.ForeignKey(get_user_model(), on_delete=models.SET(get_default_owner))

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

    def save(self):
        # print(self.cover)
        if self.pk is None:


            
            if not self.make_thumbnail():
                # set to a default thumbnail
                raise Exception('Could not create thumbnail - is the file type valid?')

            
            im = Image.open(self.cover)
            imagefit = ImageOps.fit(im, (200,300), Image.ANTIALIAS)
         

            output = BytesIO()            
            imagefit.save(output, format='JPEG', quality=90)
            output.seek(0)    
            self.cover = InMemoryUploadedFile(output,'ImageField', "%s.jpg" %self.cover.name.split('.')[0], 'image/jpeg', sys.getsizeof(output), None)


            # self.make_thumbnail()

            if not self.make_thumbnail():
                # set to a default thumbnail
                raise Exception('Could not create thumbnail - is the file type valid?')

            
        super(Book,self).save()


    def make_thumbnail(self):

        image = Image.open(self.cover)
        image.thumbnail((100,100), Image.ANTIALIAS)

        thumb_name, thumb_extension = os.path.splitext(self.cover.name)
        thumb_extension = thumb_extension.lower()

        thumb_filename = thumb_name + '_thumb' + thumb_extension
        if thumb_extension in ['.jpg', '.jpeg']:
            FTYPE = 'JPEG'
        elif thumb_extension == '.gif':
            FTYPE = 'GIF'
        elif thumb_extension == '.png':
            FTYPE = 'PNG'
        else:
            return False 

        temp_thumb = BytesIO()
        image.save(temp_thumb, FTYPE)
        temp_thumb.seek(0)

        self.thumb.save(thumb_filename, ContentFile(temp_thumb.read()), save=False)
        temp_thumb.close()

        return True
    

    def __str__(self):
        return self.title
