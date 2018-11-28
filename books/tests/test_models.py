import pytest
from mixer.backend.django import mixer
from django.db import models


@pytest.mark.django_db
class TestBook:
    def test_model(self):
        book = mixer.blend("books.Book", title="A book")
        assert book.__str__() == "A book", "Should return title"
