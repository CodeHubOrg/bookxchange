from django.contrib.auth.models import AbstractUser, UserManager
from django.db import models

# all custom user functionality from this tut
# https://wsvincent.com/django-allauth-tutorial-custom-user-model/


class CustomUserManager(UserManager):
    pass


class CustomUser(AbstractUser):
    email = models.EmailField(unique=True)
    username = models.CharField(max_length=30, unique=True)
    REQUIRED_FIELDS = ["email"]
    objects = CustomUserManager()
