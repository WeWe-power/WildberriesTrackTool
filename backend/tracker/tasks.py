import celery
from core.celery import app
from tracker.parser import get_product_info
from tracker.models import Item, User, ItemPriceRecord


class Parser(celery.Task):
    name = 'WildBerriesProductParser'

    def run(self, vendor_code, user_json):
        info = get_product_info(vendor_code)
        if info:
            ItemFabric.delay(info, user_json)
        return 'Succeeded'


class ItemCreator(celery.Task):
    name = 'ItemCreator'

    def run(self, info, user_json):
        item, __ = Item.objects.get_or_create(
            brand=info['brand'],
            vendor_code=info['vendor_code'],
            name=info['name'],
        )
        item_price_record = ItemPriceRecord.objects.create(
            price=info['price'],
            price_with_sale=info['price_with_sale'],
            item=item,
        )
        item_price_record.save()
        user = User.objects.get(id=user_json['id'])
        user.products.add(item)
        return 'Succeeded'


app.register_task(Parser())
app.register_task(ItemCreator())

ItemFabric = ItemCreator()
