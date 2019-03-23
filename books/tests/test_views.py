import pytest
from django.test import RequestFactory
from mixer.backend.django import mixer
from django.urls import reverse
from django.contrib.auth.models import AnonymousUser
from django.contrib.auth import get_user_model
from books import views
from bookx import views as views_bookx

CustomUser = get_user_model()


class TestAboutPageView:
    @pytest.mark.django_db
    def test_anonymous(self):
        req = RequestFactory().get("/about")
        resp = views_bookx.AboutPageView.as_view()(req)
        assert resp.status_code == 200, "Should be callable by anyone"


# for now leaving in both RequestFactory and Client
# for comparison


class TestBookNewView:
    def test_anonymous(self):
        req = RequestFactory().get("/")
        req.user = AnonymousUser()
        resp = views.BookNewView.as_view()(req)
        assert "login" in resp.url, "Should not allow access to anonymous"

    def test_loggedin_user(self, django_user_model):
        req = RequestFactory().get("/")
        req.user = django_user_model()
        resp = views.BookNewView.as_view()(req)
        assert resp.status_code == 200, "Authenticated user can access"

    def test_with_unauth_client(self, client):
        resp = client.get("/books/new")
        assert "login" in resp.url

    @pytest.mark.django_db
    def test_with_auth_client(self, client):
        username = "user2"
        email = "admin@example.com"
        password = "hiya"
        CustomUser.objects.create_user(
            email=email, username=username, password=password
        )
        client.login(username=email, password=password)
        resp = client.get(reverse("book_new"))
        assert resp.status_code == 200

    # failing
    # def test_with_admin_client(self, admin_client):
    #     resp = admin_client.get(reverse("book_new"))
    #     assert resp.status_code == 200
    #
    # need to rewrite with createsuperuser?


# failing
class TestBookUpdate:
    @pytest.mark.django_db
    def test_get(self, client):
        username = "user3"
        email = "user3@letmein.com"
        password = "letmein"
        user3 = CustomUser.objects.create_user(
            username=username, email=email, password=password
        )
        book = mixer.blend("books.Book", author="Kate Raworth", owner=user3)
        client.login(username=email, password=password)
        resp = client.get(reverse("book_update", kwargs={"pk": book.id}))
        assert "Add" in str(resp.content)


class TestBookListView:
    @pytest.mark.django_db
    def test_books_anonymous(self, client):
        resp = client.get(reverse("book_list"))
        assert resp.status_code == 200


class TestDetailView:
    @pytest.mark.django_db
    def test_book_detail_anonymous(self, client):
        book = mixer.blend("books.Book", author="Kate Raworth")
        resp = client.get(book.get_absolute_url())
        assert resp.status_code == 200
        assert "by Kate Raworth" in str(resp.content)
