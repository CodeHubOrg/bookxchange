import pytest
from django.contrib.auth import get_user_model


CustomUser = get_user_model()

pytestmark = pytest.mark.django_db

@pytest.fixture
def book_owner():
    return CustomUser.objects.create_user(username="user1", password="letmein")