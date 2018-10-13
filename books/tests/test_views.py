import pytest
from django.test import RequestFactory
from django.contrib.auth.models import AnonymousUser
from mixer.backend.django import mixer

pytestmark = pytest.mark.django_db

from .. import views

class TestHomePageView:
    def test_anonymous(self):
        req = RequestFactory().get('/')
        resp = views.HomePageView.as_view()(req)
        assert resp.status_code == 200, 'Should be callable by anyone'

class TestBookNewView:
    def test_anonymous(self):
        req = RequestFactory().get('/')
        req.user = AnonymousUser()
        resp = views.BookNewView.as_view()(req)
        assert 'login' in resp.url, 'Should not allow access to anonymous'

# did not manage to import CustomUser or any other
# authenticated User model so far :/

# def test_loggedin_user(self):
#         user = mixer.blend('CustomUser', is_superuser=True)
#         req = RequestFactory().get('/')
#         req.user = user
#         resp = views.BookNewView.as_view()(req)
#         assert resp.status_code == 200, 'Authenticated user can access'