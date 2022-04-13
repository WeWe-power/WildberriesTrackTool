from django.db import models
from django.contrib.auth.base_user import AbstractBaseUser
from django.contrib.auth.models import PermissionsMixin
from django.utils import timezone

from .managers import UserManager


class Item(models.Model):
    name = models.CharField(max_length=100, help_text='Наименование товара')
    brand = models.CharField(max_length=100, help_text='Название бренда')
    article = models.CharField(max_length=100, help_text='Артикул')
    price = models.IntegerField()
    price_with_sale = models.IntegerField()

    def __str__(self):
        return self.name


class User(AbstractBaseUser, PermissionsMixin):
    """User model."""
    name = models.CharField(max_length=100)
    username = models.CharField(max_length=25, unique=True)
    email = models.EmailField(unique=True)
    is_staff = models.BooleanField(default=False)
    is_superuser = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)
    date_joined = models.DateTimeField(default=timezone.now)
    products = models.ManyToManyField(Item)

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['name', 'username']

    objects = UserManager()
