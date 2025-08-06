from django.contrib import admin
from rest_framework.permissions import AllowAny
from django.urls import path, include
from drf_yasg.views import get_schema_view
from drf_yasg import openapi

# Swagger UI configuration (API documentation)
schema_view = get_schema_view(
    openapi.Info(
        title="Talk's API",
        default_version='v1',
        description="""
        This _API_ provides a solid foundation for managing users(`Individual` and `service provider`) interactions,
        messaging, business/services within the Talk platform.
        """,
    ),
    public=True,  # Make the schema public
    # Allow unauthenticated access to Swagger UI
    permission_classes=[AllowAny],
)

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', schema_view.with_ui('swagger', cache_timeout=0),
         name='schema-swagger-ui'),
    path('api/v1/auth/', include('talkapp.urls')),
    path('api/v1/products/', include('talkmarketplace.urls')),
    path('api/v1/events/', include('talkcontent.urls')),
]
