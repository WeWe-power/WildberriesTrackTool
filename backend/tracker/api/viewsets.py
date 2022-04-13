from rest_framework import generics, mixins

from tracker.api.serializers import ItemSerializer
from tracker.models import Item


class ItemListView(generics.GenericAPIView, mixins.ListModelMixin):
    queryset = Item.objects.all()
    serializer_class = ItemSerializer

    def get(self, request, *args, **kwargs):
        return self.list(request, *args, **kwargs)


class ItemRetrieveView(generics.GenericAPIView, mixins.RetrieveModelMixin):
    queryset = Item.objects.all()
    serializer_class = ItemSerializer

    def get(self, request, *args, **kwargs):
        return self.retrieve(request, *args, **kwargs)
