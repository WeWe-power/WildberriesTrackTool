from django.urls import path

from api import token_auth
from api.api_scheme import schema_view

urlpatterns = [
    path('token-auth', token_auth.GetAuthToken.as_view(), name='token-auth'),
    path('docs/swagger/', schema_view.with_ui('swagger', cache_timeout=0), name='schema-swagger-ui'),
    path('docs/redoc/', schema_view.with_ui('redoc', cache_timeout=0), name='schema-redoc'),
]
