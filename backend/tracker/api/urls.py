from django.urls import path, include

from tracker.api import viewsets

urlpatterns = [
    path('items', viewsets.ItemListCreateView.as_view(), name='item-list'),
    path('items/<str:vendor_code>', viewsets.ItemRetrieveDestroyUpdateView.as_view(), name='item-detail'),
    path('items/price_history/<str:vendor_code>', viewsets.GetItemPriceHistory.as_view(), name='item-price-history'),
    path('user/items', viewsets.UserItemList.as_view(), name='user-items'),
    path('user/items/<str:vendor_code>', viewsets.UserItemAddDelete.as_view(), name='user-items-add-delete'),
    path('user', viewsets.CreateUserView.as_view(), name='user-create'),
    path('', include('api.urls')),
]
