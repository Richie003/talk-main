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
    Service,
    ServicesImage,
    ServicesVideo,
    ServiceReview,
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
    upload_images = serializers.ListField(child=serializers.FileField(allow_empty_file=True), write_only=True)

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
            "images",
            "negotiable",
            "upload_images",   # request only
            "user",
            "approved",
            "created",
            "updated",
        ]
        read_only_fields = ["id", "slug", "created", "updated", "user", "approved"]
        extra_kwargs = {
            'upload_images': {'required': False}
        }

    def create(self, validated_data):
        images = validated_data.pop("upload_images", [])
        product = MarketPlaceProduct.objects.create(
            user=self.context["request"].user, **validated_data
        )
        for img in images:
            MarketPlaceProductImage.objects.create(product_id=product.id, image=img)
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
    upload_images = serializers.ListField(child=serializers.FileField(allow_empty_file=True), write_only=True)
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
            "images",
            "negotiable",
            "upload_images",   # request only
            "user",
            "approved",
            "created",
            "updated",
        ]

        read_only_fields = ["id", "slug", "created", "updated", "user", "approved"]
        extra_kwargs = {
            'upload_images': {'required': False}
        }

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


class ServiceImageSerializer(serializers.ModelSerializer):
    created = FormattedDateTimeField(read_only=True)
    updated = FormattedDateTimeField(read_only=True)

    class Meta:
        model = ServicesImage
        fields = [
            "id",
            "service",
            "image",
            "created",
            "updated"
        ]
        read_only_fields = ["id", "created", "updated", "service"]
        extra_kwargs = {
            'image': {'required': True}
        }

    def create(self, validated_data):
        return ServicesImage.objects.create(**validated_data)

class ServiceSerializer(serializers.ModelSerializer):
    upload_images = serializers.ListField(child=serializers.FileField(allow_empty_file=True), write_only=True, required=False)
    images = ServiceImageSerializer(source="service_images", many=True, read_only=True)
    class Meta:
        model = Service
        fields = [
            "id",
            "user",
            "title",
            "description",
            "images",
            "upload_images",
            "flat_rate",
            "negotiable"
        ]
        read_only_fields = ["id", "user"]

    def create(self, validated_data):
        images = validated_data.pop("upload_images", [])
        service = Service.objects.create(
            user=self.context["request"].user, **validated_data
        )
        for img in images:
            ServicesImage.objects.create(service_id=service.id, image=img)
        return service

    def update(self, instance, validated_data):
        images = validated_data.pop("upload_images", [])
        instance = super().update(instance, validated_data)
        for img in images:
            ServicesImage.objects.create(service=instance, image=img)
        return instance
