from rest_framework import serializers
from .models import (
    MarketPlaceProduct, 
    MarketPlaceProductImage, 
    MarketPlaceProductVideo, 
    MarketPlaceProduct,
    TakaProduct,
    TakaProductImage,
    TakaProductVideo,
    TakaReview,
    SavedItem
)
from utils.helpers import FormattedDateTimeField

class MarketPlaceProductImageSerializer(serializers.ModelSerializer):
    created = FormattedDateTimeField(read_only=True)
    updated = FormattedDateTimeField(read_only=True)

    class Meta:
        model = MarketPlaceProductImage
        fields = [
            "id",
            "product",
            "image",
            "created",
            "updated"
        ]
        read_only_fields = ["id", "created", "updated", "product"]
        extra_kwargs = {
            'image': {'required': True}
        }

    def create(self, validated_data):
        return MarketPlaceProductImage.objects.create(**validated_data)
    
class TakaProductImageSerializer(serializers.ModelSerializer):
    created = FormattedDateTimeField(read_only=True)
    updated = FormattedDateTimeField(read_only=True)

    class Meta:
        model = TakaProductImage
        fields = [
            "id",
            "product",
            "image",
            "created",
            "updated"
        ]
        read_only_fields = ["id", "created", "updated", "product"]
        extra_kwargs = {
            'image': {'required': True}
        }

    def create(self, validated_data):
        return TakaProductImage.objects.create(**validated_data)

class MarketPlaceProductSerializer(serializers.ModelSerializer):
    created = FormattedDateTimeField(read_only=True)
    updated = FormattedDateTimeField(read_only=True)
    images = MarketPlaceProductImageSerializer(source="marketplace_images", many=True, read_only=True)
    upload_images = serializers.ListSerializer(child=serializers.CharField())
    class Meta:
        model = MarketPlaceProduct
        fields = [
            "id",
            "name",
            "slug",
            "description",
            "category",
            "tag",
            "price",
            "discount",
            "negotiable",
            "images",
            "upload_images",
            "user",
            "approved",
            "created",
            "updated",
        ]

        read_only_fields = ["id", "slug", "created", "updated", "user", "approved"]
        write_only_fields = ["category",]


    
    def create(self, validated_data):
        images = validated_data.pop("upload_images", [])
        product = MarketPlaceProduct.objects.create(
            user=self.context["request"].user, **validated_data
        )
        for img in images:
            MarketPlaceProductImage.objects.create(product=product, image=img)
        return product

    def update(self, instance, validated_data):
        images = validated_data.pop("upload_images", [])
        instance = super().update(instance, validated_data)
        for img in images:
            MarketPlaceProductImage.objects.create(product=instance, image=img)
        return instance


class TakaProductSerializer(serializers.ModelSerializer):
    created = FormattedDateTimeField(read_only=True)
    updated = FormattedDateTimeField(read_only=True)
    images = TakaProductImageSerializer(source="taka_images", many=True, read_only=True)
    upload_images = serializers.ListSerializer(child=serializers.CharField())
    class Meta:
        model = TakaProduct
        fields = [
            "id",
            "name",
            "slug",
            "description",
            "category",
            "tag",
            "price",
            "discount",
            "negotiable",
            "images",
            "upload_images",
            "user",
            "approved",
            "created",
            "updated",
        ]

        read_only_fields = ["id", "slug", "created", "updated", "user", "approved"]
        write_only_fields = ["category",]


    
    def create(self, validated_data):
        images = validated_data.pop("upload_images", [])
        product = TakaProduct.objects.create(
            user=self.context["request"].user, **validated_data
        )
        for img in images:
            TakaProductImage.objects.create(product=product, image=img)
        return product

    def update(self, instance, validated_data):
        images = validated_data.pop("upload_images", [])
        instance = super().update(instance, validated_data)
        for img in images:
            TakaProductImage.objects.create(product=instance, image=img)
        return instance


class SavedItemsSerializer(serializers.ModelSerializer):
    created = FormattedDateTimeField(read_only=True)
    updated = FormattedDateTimeField(read_only=True)

    class Meta:
        model = SavedItem
        fields = [
            "id",
            "user",
            "product",
            "created",
            "updated"
        ]
        read_only_fields = ["id", "user", "created", "updated"]
