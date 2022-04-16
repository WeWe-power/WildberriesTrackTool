from django.db import models
from django.contrib.auth.base_user import AbstractBaseUser
from django.contrib.auth.models import PermissionsMixin
from django.utils import timezone

from .managers import UserManager, GetOrNoneManager


class Item(models.Model):
    vendor_code = models.CharField(max_length=100, help_text='Артикул', unique=True)
    name = models.CharField(max_length=100, help_text='Наименование товара', blank=True, null=True)
    brand = models.CharField(max_length=100, help_text='Название бренда', blank=True, null=True)
    provider = models.CharField(max_length=100, help_text='Поставщик', blank=True, null=True)

    objects = GetOrNoneManager()

    def __str__(self):
        return str(self.vendor_code)

    def get_price_info(self):
        """
        Getting price and price_with_sale fields of last ItemPriceRecord assigned to this item
        """
        price_info_obj = ItemPriceRecord.objects.filter(item=self).last()
        if price_info_obj:
            price = price_info_obj.price
            price_with_sale = price_info_obj.price_with_sale
            return {
                'price': price,
                'price_with_sale': price_with_sale
            }
        else:
            return None


class ItemPriceRecord(models.Model):
    vendor_code = models.CharField(max_length=100, help_text='Артикул')
    name = models.CharField(max_length=100, help_text='Наименование товара', blank=True, null=True)
    brand = models.CharField(max_length=100, help_text='Название бренда', blank=True, null=True)
    provider = models.CharField(max_length=100, help_text='Поставщик', blank=True, null=True)
    price = models.IntegerField()
    price_with_sale = models.IntegerField()
    time_parsed = models.DateTimeField(auto_now_add=True)
    item = models.ForeignKey(Item, on_delete=models.CASCADE, blank=True, null=True, related_name='price_info')

    def __str__(self):
        return 'Запись цены товара {} {} от {}'.format(self.item.name[:20], self.item.vendor_code, self.time_parsed)


class User(AbstractBaseUser, PermissionsMixin):
    """User model."""
    username = models.CharField(max_length=25, unique=True)
    email = models.EmailField(unique=True)
    is_staff = models.BooleanField(default=False)
    is_superuser = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)
    date_joined = models.DateTimeField(default=timezone.now)
    products = models.ManyToManyField(Item, related_name='user_items')

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username']

    objects = UserManager()
