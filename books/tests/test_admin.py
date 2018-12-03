import pytest
from mixer.backend.django import mixer
from django.contrib.auth import get_user_model


CustomUser = get_user_model()


class TestBookAdmin:
    @pytest.mark.django_db
    def test_display_author(self):
        book = mixer.blend("books.Book", author="Kate Raworth")
        display_author = book.display_author
        assert (
            display_author == "Raworth, Kate"
        ), "Should return author with lastname first"
