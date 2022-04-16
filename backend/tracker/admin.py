from django.contrib import admin
from .models import User, Item, ItemPriceRecord


@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    list_display = ("username", "email")


@admin.register(Item)
class ItemAdmin(admin.ModelAdmin):
    list_display = ("name", "brand", "vendor_code", 'provider')


@admin.register(ItemPriceRecord)
class ItemPriceRecordAdmin(admin.ModelAdmin):
    list_display = ("item", "price", "price_with_sale", 'time_parsed')

