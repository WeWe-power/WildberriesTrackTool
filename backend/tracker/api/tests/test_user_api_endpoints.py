from rest_framework import status
from django.test import TestCase, Client
from django.urls import reverse
from rest_framework.authtoken.models import Token

from tracker.models import Item, ItemPriceRecord, User
from tracker.api.serializers import ItemSerializer, ItemPriceRecordSerializer

client = Client()


class ItemsApiEndpointsTest(TestCase):
    """ Test module for GET all puppies API """

    def setUp(self):
        self.item = Item.objects.create(
            vendor_code=29,
            name='test_item',
            brand='test_brand',
            provider='test',
        )
        self.ItemPriceRecord = ItemPriceRecord.objects.create(
            vendor_code=29,
            name='test_item',
            brand='test_brand',
            provider='test',
            price='11',
            price_with_sale='12',
            item=self.item,
        )
        self.user = User.objects.create_user(
            username='test',
            email='test@email.com',
            password='test',
        )
        token = Token.objects.create(user=self.user)
        self.auth = {'HTTP_AUTHORIZATION': f'Token {token}'}

    def test_add_item_to_track_list(self):
        # Same thing as parser test
        pass

    def test_get_user_items_from_track_list(self):
        self.user.products.add(self.item)
        response = client.get(reverse('user-items'), **self.auth)
        serializer = ItemSerializer(self.item)
        self.assertEqual(response.json()[0], serializer.data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_delete_item_from_user_track_list_valid_pk(self):
        self.user.products.add(self.item)
        response = client.delete(reverse('user-items-add-delete', kwargs={'pk': 29}), **self.auth)
        self.assertEqual(list(self.user.products.all()), [])
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_delete_item_from_user_track_list_wrong_pk(self):
        self.user.products.add(self.item)
        response = client.delete(reverse('user-items-add-delete', kwargs={'pk': 20}), **self.auth)
        self.assertNotEqual(list(self.user.products.all()), [])
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)