from drf_yasg.views import get_schema_view
from drf_yasg import openapi

schema_view = get_schema_view(
    openapi.Info(
        title="Wildberries tracker API",
        default_version='v1',
        description="No description now",
        url='http://localhost:8000/',
        terms_of_service="https://www.google.com/policies/terms/",
        contact=openapi.Contact(email="example@example.gmail.com"),
        license=openapi.License(name="BSD License"),
    ),
    public=True,
)
