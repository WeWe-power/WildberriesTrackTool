from django.urls import path

from api import token_auth

urlpatterns = [
    path('token-auth', token_auth.GetAuthToken.as_view(), name='token-auth')
]
