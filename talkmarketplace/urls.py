from django.urls import path, include
from .views import (
    CategoryView,
    MarketPlaceProductCreateView,
    UploadMarketPlaceProductImageView,
    ListMarketPlaceProductsView,
    ProvidersMarketPlaceProductListView,
    MarketPlaceProductUpdateView,
    MarketPlaceProductDeleteView,

    TakaProductCreateView,
    UploadTakaProductImageView,
    ListTakaProductsView,
    ProvidersTakaProductListView,
    TakaProductUpdateView,
    TakaProductDeleteView,
    SaveItemView
)

marketplace_urlpatterns = [
    path('create-product/', MarketPlaceProductCreateView.as_view(), name='create_product'),
    path('upload-product-image/<str:product_id>', UploadMarketPlaceProductImageView.as_view(), name='upload_product_image'),
    path('list-products/', ListMarketPlaceProductsView.as_view(), name='list_products'),
    path('providers-products/', ProvidersMarketPlaceProductListView.as_view(), name='providers_products'),
    path('update-product/<slug:slug>/', MarketPlaceProductUpdateView.as_view(), name='product_detail'),
    path('delete-product/<int:id>/', MarketPlaceProductDeleteView.as_view(), name='delete_product'),
]

taka_urlpatterns = [
    path('create-product/', TakaProductCreateView.as_view(), name='create_product'),
    path('upload-product-image/<str:product_id>', UploadTakaProductImageView.as_view(), name='upload_product_image'),
    path('list-products/', ListTakaProductsView.as_view(), name='list_products'),
    path('providers-products/', ProvidersTakaProductListView.as_view(), name='providers_products'),
    path('update-product/<slug:slug>/', TakaProductUpdateView.as_view(), name='product_detail'),
    path('delete-product/<int:id>/', TakaProductDeleteView.as_view(), name='delete_product'),
]

urlpatterns = [
    path("get-categories", CategoryView.as_view(), name="get_categories"),
    path("marketplace/", include(marketplace_urlpatterns)), 
    path("taka/", include(taka_urlpatterns)),
    path("save-items/", SaveItemView.as_view())
]
