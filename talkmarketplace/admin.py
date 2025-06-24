from django.contrib import admin
from .models import (
    MarketPlaceProduct, 
    MarketPlaceProductImage, 
    MarketPlaceProductVideo, 
    MarketPlaceProductReview, 
    TakaProduct, 
    TakaProductImage, 
    TakaProductVideo, 
    TakaReview, 
    Category
)

# Register your models here.
admin.site.register(MarketPlaceProduct)
admin.site.register(MarketPlaceProductImage)
admin.site.register(MarketPlaceProductVideo)
admin.site.register(MarketPlaceProductReview)
#Taka
admin.site.register(TakaProduct)
admin.site.register(TakaProductImage)
admin.site.register(TakaProductVideo)
admin.site.register(TakaReview)
admin.site.register(Category)