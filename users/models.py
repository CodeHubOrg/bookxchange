from django.db import models
from django.contrib.auth.models import AbstractUser, UserManager, Group, Permission

class CustomUserManager(UserManager):
    pass

class CustomUser(AbstractUser):
    objects = CustomUserManager()
    '''below was so difficult to work out!!
    now discovered it was only because I spelled
    AUTH_USER_MODEL wrong in the settings!!
    -- after correction not necessary anymore, 
    just leaving it in for now for demonstration

    groups = models.ManyToManyField(
        Group,
        verbose_name='groups',
        blank=True,
        help_text=(
            'The groups this user belongs to. A user will get all permissions '
            'granted to each of their groups.'
        ),
        related_name="custom_user_set",
        related_query_name="user",
    )
    user_permissions = models.ManyToManyField(
        Permission,
        verbose_name='permissions',
        blank=True,
        related_name='custom_user_permissions'
    )'''
