import pytest
from django.contrib.auth import get_user_model

CustomUser = get_user_model()

pytestmark = pytest.mark.django_db

@pytest.fixture
def book_owner1():
    user1 = CustomUser.objects.filter(pk=1) 
    return user1 if user1.exists() else CustomUser.objects.create_user(username="user1",password="letmein",id=1,is_superuser=True)