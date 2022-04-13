from rest_framework import serializers

from tracker.models import Item, User


class ItemSerializer(serializers.ModelSerializer):
    id = serializers.IntegerField(read_only=True)

    class Meta:
        model = Item
        fields = ['id', 'name', 'brand', 'vendor_code', 'price', 'price_with_sale']

# class ItemSerializerWithoutId(serializers.ModelSerializer):
#     class Meta:
#         model = Item
#         fields = ['name', 'brand', 'vendor_code', 'price', 'price_with_sale']
