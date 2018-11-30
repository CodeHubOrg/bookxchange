from django.db import models
from django.contrib.auth.models import AbstractUser, UserManager

# all custom user functionality from this tut https://wsvincent.com/django-allauth-tutorial-custom-user-model/


class CustomUserManager(UserManager):
    pass


class CustomUser(AbstractUser):
    objects = CustomUserManager()
