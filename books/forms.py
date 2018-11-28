import os
import sys
from io import BytesIO
from PIL import Image, ImageOps

from django.core.files.uploadedfile import InMemoryUploadedFile
from django import forms
from .models import Book


class PostBookForm(forms.ModelForm):
    class Meta:
        model = Book
        fields = ("title", "author", "cover")

    def clean_author(self):
        data = self.cleaned_data.get("author")
        if len(data) <= 3:
            raise forms.ValidationError(
                "Author needs to be longer than \
                two characters"
            )
        return data

    def clean_cover(self):
        cover = self.cleaned_data.get("cover")
        if cover:
            name, extension = os.path.splitext(cover.name)
            extension = extension.lower()
            book = self.getBookIfExists()
            if not book or (book.cover != cover):
                cover = self.resize_image(cover, 200, 300, extension, 90)
        return cover

    def save(self, *args, **kwargs):
        import ipdb

        ipdb.set_trace()
        cover = self.instance.cover
        if cover:
            name, extension = os.path.splitext(cover.name)
            thumb_filename = name + "_thumb" + extension

            book = self.getBookIfExists()
            if not book or (book.thumb != thumb_filename):
                self.instance.thumb = self.make_thumbnail(
                    cover, thumb_filename, extension
                )
        else:
            self.instance.thumb = None

        return super().save(*args, **kwargs)

    def getBookIfExists(self):
        if self.instance.id:
            bookId = self.instance.id
            book = Book.objects.get(pk=bookId)
            return book
        else:
            return None

    def resize_image(self, cover, width, height, ext, quality):
        im = Image.open(cover)
        imagefit = ImageOps.fit(im, (width, height), Image.ANTIALIAS)
        ftype = self.get_file_extension(ext)

        output = BytesIO()
        imagefit.save(output, format=ftype, quality=90)
        output.seek(0)
        return InMemoryUploadedFile(
            output,
            "ImageField",
            "{0}.{1}".format(cover.name.split(".")[0], ext),
            "image/%s" % ext,
            sys.getsizeof(output),
            None,
        )

    def make_thumbnail(self, cover, name, ext):
        image = Image.open(cover)
        image.thumbnail((100, 100), Image.ANTIALIAS)

        temp_thumb = BytesIO()
        ftype = self.get_file_extension(ext)
        image.save(temp_thumb, ftype)
        temp_thumb.seek(0)

        return InMemoryUploadedFile(
            temp_thumb,
            "ImageField",
            name,
            "image/%s" % ext,
            sys.getsizeof(temp_thumb),
            None,
        )

    def get_file_extension(self, extension):
        ext_to_type = {
            ".jpg": "JPEG",
            ".jpeg": "JPEG",
            ".png": "PNG",
            ".gif": "GIF",
        }

        try:
            return ext_to_type[extension.lower()]
        except KeyError:
            valid_extensions = ", ".join(ext_to_type.keys())
            raise InvalidExtension(
                f"Could not recognise file extension {extension}. \
                Supported extensions: {valid_extensions}"
            )


class InvalidExtension(Exception):
    """Raise for invalid image extension"""
