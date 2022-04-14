from django.urls import path, include

from tracker.api import viewsets

urlpatterns = [
    path('items', viewsets.ItemListCreateView.as_view(), name='item-list'),
    path('items/<str:pk>', viewsets.ItemRetrieveDestroyUpdateView.as_view(), name='item-detail'),
    path('user/items', viewsets.UserItemList.as_view(), name='user-items'),
    path('user/items/<str:pk>', viewsets.UserItemAddDelete.as_view(), name='user-items-delete'),
    path('', include('api.urls')),
]