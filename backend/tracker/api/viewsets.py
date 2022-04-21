from django.utils.dateformat import format
from rest_framework import generics, mixins, authentication, permissions
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework import status

from tracker.api.serializers import GetUpdateItemSerializer, CreateDeleteItemSerializer, UserSerializer, \
    ItemPriceRecordSerializer
from tracker.models import Item, User
from tracker.tasks import Parser
from tracker.services import get_time

WildBerriesProductParser = Parser()


class DefaultAuth:
    """
    Mixin that oblige user to use token or session auth
    """
    authentication_classes = [authentication.SessionAuthentication, authentication.TokenAuthentication]
    permission_classes = [permissions.IsAuthenticated]


class ItemCRUDBase(generics.GenericAPIView):
    """
    Mixin that contains base variables for CRUD views for model items
    """
    queryset = Item.objects.all()
    lookup_field = 'vendor_code'
    lookup_url_kwarg = 'vendor_code'

    def get_serializer_class(self):
        if self.request.method == 'GET' or self.request.method == 'PUT' or self.request.method == 'PATCH':
            return GetUpdateItemSerializer
        if self.request.method == 'DELETE' or self.request.method == 'POST':
            return CreateDeleteItemSerializer


class ItemListCreateView(
    ItemCRUDBase, mixins.ListModelMixin, mixins.CreateModelMixin, DefaultAuth
):

    def get(self, request, *args, **kwargs):
        """
        Shows all items
        """
        return self.list(request, *args, **kwargs)

    def post(self, request, *args, **kwargs):
        """
        Create new item
        """
        return self.create(request, *args, **kwargs)

    def get_serializer_class(self):
        if self.request.method == 'GET':
            return GetUpdateItemSerializer
        if self.request.method == 'POST':
            return CreateDeleteItemSerializer


class ItemRetrieveDestroyUpdateView(
    ItemCRUDBase, mixins.RetrieveModelMixin, mixins.DestroyModelMixin, mixins.UpdateModelMixin, DefaultAuth
):

    def get(self, request, *args, **kwargs):
        """
        Show details of item
        """
        return self.retrieve(request, *args, **kwargs)

    def delete(self, request, *args, **kwargs):
        """
        Deletes item
        """
        return self.destroy(request, *args, **kwargs)

    def put(self, request, *args, **kwargs):
        """
        Updates item
        """
        return self.update(request, *args, **kwargs)

    def patch(self, request, *args, **kwargs):
        """
        Partially updates an item
        """
        return self.partial_update(request, *args, **kwargs)

    def retrieve(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = self.get_serializer(instance)
        return Response(serializer.data)


class CreateUserView(generics.CreateAPIView):
    """
    View that holds user creation
    """
    model = User
    permission_classes = [
        permissions.AllowAny
    ]
    serializer_class = UserSerializer


class UserItemList(
    ItemCRUDBase, mixins.ListModelMixin, DefaultAuth
):
    """
    Shows list of all items tracked by user
    """

    def get(self, request, *args, **kwargs):
        user = self.request.user
        items = user.products.all()
        serializer = GetUpdateItemSerializer(items, many=True)
        return Response(serializer.data)


class UserItemAddDelete(
    APIView, DefaultAuth
):

    def post(self, request, *args, **kwargs):
        """
        Adds item to user tracking list and parses it
        """
        item_id = self.kwargs['vendor_code']
        item = Item.objects.get_or_none(vendor_code=item_id)
        user = self.request.user
        if item is None:
            serializer = UserSerializer(user)
            WildBerriesProductParser.delay(self.kwargs['vendor_code'], serializer.data)
            return Response('Started process of adding item to your tracking list, it may take some time....',
                            status=status.HTTP_202_ACCEPTED)
        elif item not in user.products.all():
            user.products.add(item)
            return Response('Item added', status=status.HTTP_200_OK)
        return Response('You already have item with this article in your tracking list', status=status.HTTP_200_OK)

    def delete(self, request, *args, **kwargs):
        """
        Deletes item from user tracking list
        """
        vendor_code = self.kwargs['vendor_code']
        item = Item.objects.get_or_none(vendor_code=vendor_code)
        if item:
            user = self.request.user
            user.products.remove(item)
            return Response('Item with article {} deleted from your tracking list'.format(vendor_code),
                            status=status.HTTP_200_OK)
        return Response('Item with vendor code {} not found'.format(vendor_code), status=status.HTTP_404_NOT_FOUND)


class GetItemPriceHistory(
    APIView, DefaultAuth
):
    """
    Returns item price history
    """

    def get(self, request, *args, **kwargs):
        vendor_code = self.kwargs['vendor_code']
        date_formats = ["%d/%m/%Y", "%m/%Y", "%Y"]

        start_time = get_time(self.request.query_params.get('start_time'), date_formats)
        end_time = get_time(self.request.query_params.get('end_time'), date_formats)
        if end_time is None or start_time is None:
            return Response('Invalid data')

        item = Item.objects.get_or_none(vendor_code=vendor_code)
        if item is None:
            return Response('Item with vendor code {} not found'.format(vendor_code), status=status.HTTP_404_NOT_FOUND)

        prices_dict = {}
        for item_price_record in item.price_info.order_by('time_parsed'):
            item_price_record_date = format(item_price_record.time_parsed, 'U')
            if start_time < float(item_price_record_date) < end_time:
                serializer = ItemPriceRecordSerializer(item_price_record)
                prices_dict[str(item_price_record.time_parsed)] = serializer.data
        return Response(prices_dict)
