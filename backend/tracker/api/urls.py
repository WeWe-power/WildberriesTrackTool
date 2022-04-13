from django.urls import path, include

from tracker.api import viewsets

urlpatterns = [
    path('items', viewsets.ItemListView.as_view(), name='item-list'),
    path('items/<str:pk>', viewsets.ItemRetrieveView.as_view(), name='item-detail'),
    path('', include('api.urls'))
]
