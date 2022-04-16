import celery
from celery import shared_task

from core.celery import app
from tracker.parser import get_product_info
from tracker.models import Item, User, ItemPriceRecord
from django.utils import timezone


class Parser(celery.Task):
    """
    Task that parses info about wildberries card page using product vendor_code
    returns dict containing info about product
    """
    name = 'WildBerriesProductParser'

    def run(self, vendor_code, user_json=None):
        info = get_product_info(vendor_code)
        if info:
            ItemFabric.delay(info, user_json)
            return info
        return "Unsuccessfully, can't find item with vendor code {}".format(vendor_code)


class ItemCreator(celery.Task):
    """
    Task that creates an item instance if not exist or gets it if it exist,
    Then create a item price record instance and assign it to item instance,
    After assign an item instance to a request user instance
    """
    name = 'ItemCreator'

    def run(self, info, user_json=None):
        item, __ = Item.objects.get_or_create(
            vendor_code=info['vendor_code'],
        )

        if (item.brand != info['brand']) or (item.name != info['name']) or (item.provider != info['provider']):
            item.brand = info['brand']
            item.name = info['name']
            item.provider = info['provider']
            item.save()

        item_price_record, created = ItemPriceRecord.objects.get_or_create(
            brand=info['brand'],
            name=info['name'],
            provider=info['provider'],
            price=info['price'],
            price_with_sale=info['price_with_sale'],
            item=item,
        )

        # If called by user, we need to assign an item to a user he wants to track
        if user_json:
            user = User.objects.get(id=user_json['id'])
            user.products.add(item)

        if created:
            item_price_record.time_parsed = timezone.now
            return 'Succeeded'

        return 'Already have an item price record with same price values'


@shared_task
def periodic_info_collection():
    """
    Task that collects data for every instance in item
    """
    for item in Item.objects.only('vendor_code'):
        WildBerriesParser.delay(item.vendor_code)

    return 'Succeeded'


app.register_task(Parser())
app.register_task(ItemCreator())

ItemFabric = ItemCreator()
WildBerriesParser = Parser()
