from django.urls import path, include
from .views import (
    MarketPlaceProductCreateView,
    ListMarketPlaceProductsView,
    ProvidersMarketPlaceProductListView,
    MarketPlaceProductUpdateView,
    MarketPlaceProductDeleteView,

    TakaProductCreateView,
    ListTakaProductsView,
    ProvidersTakaProductListView,
    TakaProductUpdateView,
    TakaProductDeleteView,
    DeleteSavedItemView,
    SaveItemView
)
marketplace_urlpatterns = [
    path('create-product/', MarketPlaceProductCreateView.as_view(), name='create_product'),
    path('list-products/', ListMarketPlaceProductsView.as_view(), name='list_products'),
    path('providers-products/', ProvidersMarketPlaceProductListView.as_view(), name='providers_products'),
    path('update-product/<slug:slug>/', MarketPlaceProductUpdateView.as_view(), name='product_detail'),
    path('delete-product/<int:id>/', MarketPlaceProductDeleteView.as_view(), name='delete_product'),
]

taka_urlpatterns = [
    path('create-product/', TakaProductCreateView.as_view(), name='create_product'),
    path('list-products/', ListTakaProductsView.as_view(), name='list_products'),
    path('providers-products/', ProvidersTakaProductListView.as_view(), name='providers_products'),
    path('update-product/<slug:slug>/', TakaProductUpdateView.as_view(), name='product_detail'),
    path('delete-product/<int:id>/', TakaProductDeleteView.as_view(), name='delete_product'),
]

urlpatterns = [
    path("marketplace/", include(marketplace_urlpatterns)),
    path("taka/", include(taka_urlpatterns)),
    path("save-items/", SaveItemView.as_view()),
    path('inventory/saved-items/<int:product_id>/delete/', DeleteSavedItemView.as_view(), name='delete_saved_item'),
]
