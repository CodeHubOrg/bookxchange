import pytest
from django.test import RequestFactory
from django.contrib.auth.models import AnonymousUser
from django.contrib.auth import get_user_model
from books import views

CustomUser = get_user_model()

pytestmark = pytest.mark.django_db


class TestHomePageView:
    def test_anonymous(self):
        req = RequestFactory().get('/')
        resp = views.HomePageView.as_view()(req)
        assert resp.status_code == 200, 'Should be callable by anyone'

# for now leaving in both RequestFactory and Client 
# for comparison

class TestBookNewView:
    def test_anonymous(self):
        req = RequestFactory().get('/')
        req.user = AnonymousUser()
        resp = views.BookNewView.as_view()(req)
        assert 'login' in resp.url, 'Should not allow access to anonymous'

    def test_loggedin_user(self):        
        req = RequestFactory().get('/')
        req.user = CustomUser()
        resp = views.BookNewView.as_view()(req)
        assert resp.status_code == 200, 'Authenticated user can access'

    def test_with_unauth_client(self, client):
        resp = client.get('/book/new')
        assert 'login' in resp.url

    def test_with_auth_client(self, client):
        username = "user1"
        password = "hiya"
        CustomUser.objects.create_user(username=username, password=password)
        client.login(username=username, password=password)
        resp = client.get('/book/new')
        assert resp.status_code == 200

    def test_with_auth_client(self, admin_client):
        resp = admin_client.get('/book/new')
        assert resp.status_code == 200
