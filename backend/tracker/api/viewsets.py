from rest_framework import generics, mixins, authentication, permissions

from tracker.api.serializers import ItemSerializer
from tracker.models import Item


class DefaultAuth(generics.GenericAPIView):
    """
    View that oblige user to use token or session auth
    """
    authentication_classes = [authentication.SessionAuthentication, authentication.TokenAuthentication]
    permission_classes = [permissions.IsAuthenticated]


class ItemCRUDBase(generics.GenericAPIView):
    """
    View that contains base variables for CRUD views for model items
    """
    queryset = Item.objects.all()
    serializer_class = ItemSerializer
    lookup_field = 'pk'


class ItemListView(ItemCRUDBase, mixins.ListModelMixin, DefaultAuth):
    """
    Shows all items
    """
    def get(self, request, *args, **kwargs):
        return self.list(request, *args, **kwargs)


class ItemRetrieveView(ItemCRUDBase, mixins.RetrieveModelMixin, DefaultAuth):
    """
    Show details of one item by pk
    """
    def get(self, request, *args, **kwargs):
        return self.retrieve(request, *args, **kwargs)
