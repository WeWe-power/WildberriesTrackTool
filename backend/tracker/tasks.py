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
            return 'Succeeded'
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
            brand=info['brand'],
            vendor_code=info['vendor_code'],
            name=info['name'],
            provider=info['provider'],
        )
        item_price_record = ItemPriceRecord.objects.create(
            price=info['price'],
            price_with_sale=info['price_with_sale'],
            time_parsed=timezone.now,
            item=item,
        )
        item_price_record.save()

        # If called by user, we need to assign an item to a user he wants to track
        if user_json:
            user = User.objects.get(id=user_json['id'])
            user.products.add(item)
        # If called automatically by scheduled task for info parsing, we dont need to make assignment
        else:
            pass

        return 'Succeeded'


@shared_task
def periodic_info_collection():
    """
    Task that collects data for every instance in item
    """
    for vendor_code in Item.objects.only('vendor_code'):
        WildBerriesParser(vendor_code)

    return 'Succeeded'


app.register_task(Parser())
app.register_task(ItemCreator())

ItemFabric = ItemCreator()
WildBerriesParser = Parser()
