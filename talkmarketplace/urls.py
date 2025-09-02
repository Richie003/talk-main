from django.urls import path, include
from .views import (
    MarketPlaceProductCreateView,
    ListMarketPlaceProductsView,
    ProvidersMarketPlaceProductListView,
    MarketPlaceProductDetailView,
    MarketPlaceProductUpdateView,
    MarketPlaceProductDeleteView,

    TakaProductCreateView,
    ListTakaProductsView,
    ProvidersTakaProductListView,
    TakaProductDetailView,
    TakaProductUpdateView,
    TakaProductDeleteView,
    SaveItemView,
    ServiceCreateView,
    ListServicesView,
    ProvidersServicesListView,
    ServiceDetailView,
    ServiceUpdateView,
    ServiceDeleteView
)

marketplace_urlpatterns = [
    path('create-product/', MarketPlaceProductCreateView.as_view(), name='create_product'),
    path('list-products/', ListMarketPlaceProductsView.as_view(), name='list_products'),
    path('product-detail/<slug:slug>/', MarketPlaceProductDetailView.as_view(), name='product_detail'),
    path('providers-products/', ProvidersMarketPlaceProductListView.as_view(), name='providers_products'),
    path('update-product/<slug:slug>/', MarketPlaceProductUpdateView.as_view(), name='product_detail'),
    path('delete-product/<str:id>/', MarketPlaceProductDeleteView.as_view(), name='delete_product'),
]

taka_urlpatterns = [
    path('create-product/', TakaProductCreateView.as_view(), name='create_product'),
    path('list-products/', ListTakaProductsView.as_view(), name='list_products'),
    path('product-detail/<slug:slug>/', TakaProductDetailView.as_view(), name='product_detail'),
    path('providers-products/', ProvidersTakaProductListView.as_view(), name='providers_products'),
    path('update-product/<slug:slug>/', TakaProductUpdateView.as_view(), name='product_detail'),
    path('delete-product/<str:id>/', TakaProductDeleteView.as_view(), name='delete_product'),
]

service_urlpatterns = [
    path('create-service/', ServiceCreateView.as_view(), name='create_service'),
    path('list-services/', ListServicesView.as_view(), name='list_services'),
    path('service-detail/<slug:slug>/', ServiceDetailView.as_view(), name='service_detail'),
    path('providers-services/', ProvidersServicesListView.as_view(), name='providers_services'),
    path('update-service/<slug:slug>/', ServiceUpdateView.as_view(), name='service_detail'),
    path('delete-service/<str:id>/', ServiceDeleteView.as_view(), name='delete_service'),
]

urlpatterns = [
    path("marketplace/", include(marketplace_urlpatterns)), 
    path("taka/", include(taka_urlpatterns)),
    path("services/", include(service_urlpatterns)),
    path("save-items/", SaveItemView.as_view())
]
