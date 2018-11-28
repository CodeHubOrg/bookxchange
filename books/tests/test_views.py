import pytest
from django.test import RequestFactory
from mixer.backend.django import mixer
from django.urls import reverse
from django.contrib.auth.models import AnonymousUser
from django.contrib.auth import get_user_model
from books import views

CustomUser = get_user_model()


class TestHomePageView:
    @pytest.mark.django_db
    def test_anonymous(self):
        req = RequestFactory().get("/")
        resp = views.HomePageView.as_view()(req)
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
        resp = client.get("/book/new")
        assert "login" in resp.url

    @pytest.mark.django_db
    def test_with_auth_client(self, client):
        username = "user2"
        password = "hiya"
        CustomUser.objects.create_user(username=username, password=password)
        client.login(username=username, password=password)
        resp = client.get("/book/new")
        assert resp.status_code == 200

    def test_with_admin_client(self, admin_client):
        resp = admin_client.get("/book/new")
        assert resp.status_code == 200


class TestBookUpdate:
    @pytest.mark.django_db
    def test_get(self, client):
        username = "user3"
        password = "letmein"
        user3 = CustomUser.objects.create_user(username=username, password=password)
        book = mixer.blend("books.Book", author="Kate Raworth", owner=user3)
        client.login(username=username, password=password)
        resp = client.get(book.update_url)
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
