import celery
from core.celery import app
from tracker.parser import get_product_info
from tracker.models import Item, User


class Parser(celery.Task):
    name = 'WildBerriesProductParser'

    def run(self, vendor_code, user_json):
        info = get_product_info(vendor_code)
        if info:
            item = Item.objects.create(
                brand=info['brand'],
                vendor_code=info['vendor_code'],
                name=info['name'],
                price=info['price'],
                price_with_sale=info['price_with_sale'],
            )
            item.save()
            user = User.objects.get(id=user_json['id'])
            user.products.add(item)
            #NEED TO DECOMPOSITE THIS TASK



app.register_task(Parser())
