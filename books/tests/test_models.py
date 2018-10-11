from books.models import Book

# pytestmark = pytest.mark.django_db


# class TestBookModel:

#     def test_save(self):
#         book = Book.objects.create(
#                 title="A book",
#                 author="Anonymous",
#                 cover="covers/gopher.png",
#                 published_date = "2018-10-04 01:06:10.607916+00"
#             )
#         assert book.title == "A book"
#         assert book.author == "Anonymous"
#         assert book.cover == "covers/gopher.png"
#         assert book.published_date == "2018-10-04 01:06:10.607916+00"

from django.test import TestCase


# models test
class BookTest(TestCase):

    def create_book(
            self, 
            title="A book",
            author="Anonymous",
            cover="covers/gopher.png",
            published_date = "2018-10-04 01:06:10.607916+00"):
        return Book.objects.create(
            title=title, 
            author=author,
            cover=cover,
            published_date=published_date,
            )

    def test_book_creation(self):
        b = self.create_book()
        self.assertTrue(isinstance(b, Book))
        self.assertEqual(b.__str__(), b.title)

