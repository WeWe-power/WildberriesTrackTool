from rest_framework import generics, mixins, authentication, permissions
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework import status

from tracker.api.serializers import ItemSerializer, UserSerializer
from tracker.models import Item

from tracker.tasks import Parser

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
    serializer_class = ItemSerializer
    lookup_field = 'pk'


class ItemListCreateView(
    ItemCRUDBase, mixins.ListModelMixin, mixins.CreateModelMixin, DefaultAuth
):
    """
    GET: Shows all items
    POST: Create new item
    """

    def get(self, request, *args, **kwargs):
        return self.list(request, *args, **kwargs)

    def post(self, request, *args, **kwargs):
        return self.create(request, *args, **kwargs)


class ItemRetrieveDestroyUpdateView(
    ItemCRUDBase, mixins.RetrieveModelMixin, mixins.DestroyModelMixin, mixins.UpdateModelMixin, DefaultAuth
):
    """
    GET: Show details of item
    DELETE: Deletes item
    PATCH: updates item
    """

    def get(self, request, *args, **kwargs):
        return self.retrieve(request, *args, **kwargs)

    def delete(self, request, *args, **kwargs):
        return self.destroy(request, *args, **kwargs)

    def put(self, request, *args, **kwargs):
        return self.update(request, *args, **kwargs)

    def patch(self, request, *args, **kwargs):
        return self.partial_update(request, *args, **kwargs)


class UserItemList(
    ItemCRUDBase, mixins.ListModelMixin, DefaultAuth
):
    """
    GET: Shows list of all items tracked by user
    """

    def get(self, request, *args, **kwargs):
        user = self.request.user
        items = user.products.all()
        serializer = ItemSerializer(items, many=True)
        return Response(serializer.data)


class UserItemAddDelete(
    APIView, DefaultAuth
):
    """
    POST: View that adds item to user tracking list and parses it
    DELETE: Delete item from
    """

    def post(self, request, *args, **kwargs):
        item_id = self.kwargs['pk']
        item = Item.objects.get_or_none(vendor_code=item_id)
        if item is None:
            serializer = UserSerializer(self.request.user)
            WildBerriesProductParser.delay(self.kwargs['pk'], serializer.data)
            return Response('Started process of adding item to your tracking list, it may take some time....', status=status.HTTP_202_ACCEPTED)
        return Response('You already have item with this article in your tracking list', status=status.HTTP_200_OK)

    def delete(self, request, *args, **kwargs):
        item_id = self.kwargs['pk']
        item = Item.objects.get(vendor_code=item_id)
        user = self.request.user
        user.products.remove(item)
        return Response('Item with article {} deleted from your tracking list'.format(item_id), status=status.HTTP_200_OK)
