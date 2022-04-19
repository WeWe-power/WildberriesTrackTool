from rest_framework import serializers

from tracker.models import Item, User, ItemPriceRecord


class GetUpdateItemSerializer(serializers.ModelSerializer):
    id = serializers.IntegerField(read_only=True)
    price = serializers.IntegerField(read_only=True)
    price_with_sale = serializers.IntegerField(read_only=True)
    vendor_code = serializers.CharField(read_only=True)
    name = serializers.CharField(required=False)
    brand = serializers.CharField(required=False)
    provider = serializers.CharField(required=False)

    class Meta:
        model = Item
        fields = ['id', 'name', 'brand', 'vendor_code', 'price', 'price_with_sale', 'provider']

    def to_representation(self, instance):
        data = super().to_representation(instance)
        price_info_dict = instance.get_price_info()
        if price_info_dict:
            data["price"] = price_info_dict['price']
            data["price_with_sale"] = price_info_dict['price_with_sale']
        else:
            data["price"] = 0
            data["price_with_sale"] = 0
        return data


class CreateDeleteItemSerializer(serializers.ModelSerializer):
    class Meta:
        model = Item
        fields = ['vendor_code']


class UserSerializer(serializers.ModelSerializer):
    id = serializers.IntegerField(read_only=True)
    password = serializers.CharField(write_only=True)

    def create(self, validated_data):
        user = User.objects.create_user(
            username=validated_data['username'],
            email=validated_data['email'],
            password=validated_data['password'],
        )

        return user

    class Meta:
        model = User
        fields = ("id", "username", "email", "password",)


class ItemPriceRecordSerializer(serializers.ModelSerializer):
    class Meta:
        model = ItemPriceRecord
        fields = ['name', 'brand', 'vendor_code', 'price', 'price_with_sale']
