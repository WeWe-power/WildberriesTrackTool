from rest_framework import serializers

from tracker.models import Item, User, ItemPriceRecord


class ItemSerializer(serializers.ModelSerializer):
    id = serializers.IntegerField(read_only=True)
    price = serializers.IntegerField(read_only=True)
    price_with_sale = serializers.IntegerField(read_only=True)

    class Meta:
        model = Item
        fields = ['id', 'name', 'brand', 'vendor_code', 'price', 'price_with_sale', 'provider']

    def to_representation(self, instance):
        data = super().to_representation(instance)
        price_info_dict = instance.get_price_info()
        data["price"] = price_info_dict['price']
        data["price_with_sale"] = price_info_dict['price_with_sale']
        return data


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
