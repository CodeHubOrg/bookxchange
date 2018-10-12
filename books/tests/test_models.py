import pytest
from mixer.backend.django import mixer
from django.db import models

pytestmark = pytest.mark.django_db

class TestBook:
    def test_model(self):
        obj = mixer.blend('books.Book', title="A book")
        assert obj.__str__() == "A book", 'Should return title'
