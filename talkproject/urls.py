from django.contrib import admin
from rest_framework.permissions import AllowAny
from django.urls import path, include
from drf_spectacular.views import SpectacularAPIView, SpectacularSwaggerView

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/schema/', SpectacularAPIView.as_view(), name='schema'),
    path('', SpectacularSwaggerView.as_view(), name='swagger-ui'),
    path('api/v1/auth/', include('talkapp.urls')),
    path('api/v1/products/', include('talkmarketplace.urls')),
    path('api/v1/', include('talkcontent.urls')),
]
