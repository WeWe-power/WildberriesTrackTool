from rest_framework import generics, mixins, authentication, permissions
from rest_framework.response import Response
from rest_framework.views import APIView

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
    Shows list of all items tracked by user
    """

    def get(self, request, *args, **kwargs):
        user = self.request.user
        items = user.products.all()
        serializer = ItemSerializer(items, many=True)
        return Response(serializer.data)


class UserItemAdd(
    APIView, DefaultAuth
):

    def post(self, request, *args, **kwargs):
        serializer = UserSerializer(self.request.user)
        WildBerriesProductParser.delay(self.kwargs['pk'], serializer.data)
