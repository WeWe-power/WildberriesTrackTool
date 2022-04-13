from rest_framework import serializers

from tracker.models import Item, User


class ItemSerializer(serializers.ModelSerializer):
    id = serializers.IntegerField(read_only=True)

    class Meta:
        model = Item
        fields = ['id', 'name', 'brand', 'vendor_code', 'price', 'price_with_sale']


class UserSerializer(serializers.ModelSerializer):
    id = serializers.IntegerField(read_only=True)

    class Meta:
        model = User
        fields = '__all__'
