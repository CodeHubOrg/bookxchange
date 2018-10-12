import pytest 
from django.contrib.admin.sites import AdminSite
from mixer.backend.django import mixer
from django.db import models

pytestmark = pytest.mark.django_db

from .. import admin
from .. import models

class TestBookAdmin:
    def test_display_author(self):
        site = AdminSite()
        book_admin = admin.BookAdmin(models.Book, site) 
        obj = mixer.blend('books.Book', author="Kate Raworth")
        display_author = book_admin.display_author(obj)
        assert display_author == "Raworth, Kate", "Should return author with lastname first"
