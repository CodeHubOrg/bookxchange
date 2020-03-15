import os
import sys
import uuid
from urllib import request as urlreq
from io import BytesIO
from PIL import Image
from django.conf import settings
from django.core.files.uploadedfile import InMemoryUploadedFile
from django import forms
from .models import Book, Comment

class PostBookForm(forms.ModelForm):
    openlibcover = forms.CharField(max_length=200, widget=forms.HiddenInput())

    class Meta:
        model = Book
        fields = (
            "isbn",
            "title",
            "author",
            "cover",
            "description",
            "year_published",
            "category",
            "openlibcover",
            "at_framework",
        )
        widgets = {
            "title": forms.TextInput(attrs={"class": "uk-input"}),
            "author": forms.TextInput(attrs={"class": "uk-input"}),
            "isbn": forms.TextInput(attrs={"class": "uk-input"}),
            "description": forms.Textarea(attrs={"class": "uk-textarea"}),
            "category": forms.Select(attrs={"class": "uk-select"}),
        }

    def __init__(self, *args, **kwargs):
        # first call parent's constructor
        super(PostBookForm, self).__init__(*args, **kwargs)
        self.fields["description"].required = False
        self.fields["openlibcover"].required = False

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
        if cover and "cover" in self.changed_data:
            name, extension = os.path.splitext(cover.name)
            extension = extension.lower()
            cover = self.resize_image(cover, 200, 300, extension, 90)
        return cover

    def clean_isbn(self):
        isbn = self.cleaned_data.get("isbn")
        return isbn and isbn.replace("-", "")

    def save(self, *args, **kwargs):
        cover = self.instance.cover
        openlib = self.cleaned_data.get("openlibcover")
        if cover and "cover" in self.changed_data:
            cover = self.instance.cover
            name, extension = os.path.splitext(cover.name)
            thumb_filename = f"{name}_thumb{extension}"
            self.instance.thumb = self.make_thumbnail(
                cover, thumb_filename, extension
            )
        if not cover and openlib:
            openlib_file = os.path.basename(openlib)
            self.instance.cover = f"covers/{openlib_file}"
            openlib_local = f"{settings.BASE_DIR}/media/covers/{openlib_file}"
            urlreq.urlretrieve(openlib, openlib_local)
            cover = self.instance.cover
            name, extension = os.path.splitext(openlib_file)
            thumb_filename = f"{name}_thumb{extension}"
            self.instance.thumb = self.make_thumbnail(
                cover, thumb_filename, extension
            )
        if not cover and "cover" in self.changed_data:
            self.instance.thumb = None
        return super().save(*args, **kwargs)

    def resize_image(self, cover, width, height, ext, quality):
        covername = cover.name.split(".")[0]
        img_id = uuid.uuid4().hex
        im = Image.open(cover)
        im.thumbnail((width, height), Image.ANTIALIAS)
        ftype = self.get_file_extension(ext)
        output = BytesIO()
        im.save(output, format=ftype, quality=90)
        output.seek(0)
        return InMemoryUploadedFile(
            output,
            "ImageField",
            f"{covername}_{img_id}{ext}",
            "image/%s" % ext,
            sys.getsizeof(output),
            None,
        )

    def make_thumbnail(self, cover, name, ext):
        image = Image.open(cover)
        image.thumbnail((50, 150), Image.ANTIALIAS)

        temp_thumb = BytesIO()
        ftype = self.get_file_extension(ext)
        image.save(temp_thumb, ftype)
        temp_thumb.seek(0)

        return InMemoryUploadedFile(
            temp_thumb,
            "ImageField",
            name,
            f"image/{ext}",
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


class PostCommentForm(forms.ModelForm):

    class Meta:
        model = Comment
        fields = (
            "comment",
        )
        widgets = {
            "comment": forms.Textarea(attrs={"class": "uk-textarea"})
        }
