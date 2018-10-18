import pytest 
from django.contrib.admin.sites import AdminSite
from mixer.backend.django import mixer
from django.contrib.auth import get_user_model
from django.db import models
from books import admin, models

CustomUser = get_user_model()


@pytest.mark.django_db
class TestBookAdmin:
    def test_display_author(self, book_owner1):
        user1 = book_owner1
        site = AdminSite()
        book_admin = admin.BookAdmin(models.Book, site) 
        obj = mixer.blend('books.Book', author="Kate Raworth")
        display_author = obj.display_author
        assert display_author == "Raworth, Kate", "Should return author with lastname first"
