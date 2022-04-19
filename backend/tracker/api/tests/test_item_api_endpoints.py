from rest_framework import status
from django.test import TestCase, Client
from django.urls import reverse
from rest_framework.authtoken.models import Token

from tracker.models import Item, ItemPriceRecord, User
from tracker.api.serializers import GetUpdateItemSerializer, CreateDeleteItemSerializer, ItemPriceRecordSerializer

client = Client()


class TestData(TestCase):
    """
    Setting test data for all test cases
    """

    @classmethod
    def setUpTestData(cls):
        item = Item.objects.create(
            vendor_code=28,
            name='test_item',
            brand='test_brand',
            provider='test',
        )
        ItemPriceRecord.objects.create(
            vendor_code=28,
            name='test_item',
            brand='test_brand',
            provider='test',
            price='10',
            price_with_sale='8',
            item=item,
        )
        item = Item.objects.create(
            vendor_code=29,
            name='test_item',
            brand='test_brand',
            provider='test',
        )
        ItemPriceRecord.objects.create(
            vendor_code=29,
            name='test_item',
            brand='test_brand',
            provider='test',
            price='11',
            price_with_sale='12',
            item=item,
        )
        user = User.objects.create_user(
            username='test',
            email='test@email.com',
            password='test',
        )
        Token.objects.create(user=user)

    @staticmethod
    def get_auth_header():
        token, created = Token.objects.get_or_create(user_id=1)
        auth_header = {'HTTP_AUTHORIZATION': f'Token {token}'}
        return auth_header


class GetItemsListTest(TestData):
    """
    Test GET list of items
    """

    def test_get_all_items(self):
        response = client.get(reverse('item-list'), **self.get_auth_header())
        items = Item.objects.all()
        serializer = GetUpdateItemSerializer(items, many=True)
        self.assertEqual(response.data, serializer.data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)


class CreateItemTest(TestData):
    """
    Test create item
    """

    def test_create_item_valid_vendor_code(self):
        vendor_code = 1
        data = {'vendor_code': vendor_code}
        response = client.post(reverse('item-list'), data=data, **self.get_auth_header())
        item = Item.objects.get_or_none(vendor_code=vendor_code)
        serializer = CreateDeleteItemSerializer(item)
        self.assertTrue(item)
        self.assertEqual(response.data, serializer.data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_create_item_invalid_vendor_code(self):
        data = {'vendor_code': ''}
        response = client.post(reverse('item-list'), data=data, **self.get_auth_header())
        self.assertEqual(response.data['vendor_code'][0].title(), 'This Field May Not Be Blank.')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)


class UpdateItemTest(TestData):
    """
    Test create item
    """

    def test_update_item(self):
        data = {
            'name': 'test_item_new',
            'brand': 'test_brand_new',
            'provider': 'test_new',
        }
        response = client.put(reverse('item-detail', kwargs={'vendor_code': 28}), data=data,
                              content_type='application/json', **self.get_auth_header())
        item = Item.objects.get(vendor_code=28)
        serializer = GetUpdateItemSerializer(item)
        self.assertEqual(response.data, serializer.data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_partial_update_item(self):
        data = {
            'name': 'test_item_new',
        }
        response = client.patch(reverse('item-detail', kwargs={'vendor_code': 28}), data=data,
                                content_type='application/json', **self.get_auth_header())
        item = Item.objects.get(vendor_code=28)
        serializer = GetUpdateItemSerializer(item)
        self.assertEqual(response.data, serializer.data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)


class DeleteItemTest(TestData):
    """
    Test DELETE item details
    """

    def test_item_delete_valid_vendor_code(self):
        response = client.delete(reverse('item-detail', kwargs={'vendor_code': 28}), **self.get_auth_header())
        item = Item.objects.get_or_none(vendor_code=28)
        self.assertFalse(item)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)

    def test_item_delete_invalid_vendor_code(self):
        response = client.delete(reverse('item-detail', kwargs={'vendor_code': 29}), **self.get_auth_header())
        item = Item.objects.get_or_none(vendor_code=28)
        self.assertTrue(item)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)


class GetItemDetailsTest(TestData):
    """
    Test GET item details
    """

    def test_get_item_details_valid_vendor_code(self):
        response = client.get(reverse('item-detail', kwargs={'vendor_code': 28}), **self.get_auth_header())
        item = Item.objects.get(id=1)
        serializer = GetUpdateItemSerializer(item)
        self.assertEqual(response.data, serializer.data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_get_item_details_invalid_vendor_code(self):
        response = client.get(reverse('item-detail', kwargs={'vendor_code': 20}), **self.get_auth_header())
        self.assertEqual(response.data['detail'].title(), 'Not Found.')
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)


class GetItemPriceHistoryTest(TestData):
    """
    Test GET item price history
    """

    def test_get_item_price_history_valid_vendor_code(self):
        response = client.get(reverse('item-price-history', kwargs={'vendor_code': 28}), **self.get_auth_header())
        item = Item.objects.get(id=1)
        item_record = ItemPriceRecord.objects.get(item=item)
        serializer = ItemPriceRecordSerializer(item_record)
        price_history = {str(item_record.time_parsed): serializer.data}
        self.assertEqual(response.data, price_history)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_get_item_price_history_invalid_vendor_code(self):
        response = client.get(reverse('item-price-history', kwargs={'vendor_code': 20}), **self.get_auth_header())
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
