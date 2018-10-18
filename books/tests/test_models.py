import pytest
from mixer.backend.django import mixer
from django.db import models


@pytest.mark.django_db
class TestBook:
    def test_model(self, book_owner1):
        user1 = book_owner1
        obj = mixer.blend('books.Book', title="A book")
        assert obj.__str__() == "A book", 'Should return title'
