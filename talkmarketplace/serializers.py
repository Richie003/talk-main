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

class MarketPlaceProductSerializer(serializers.ModelSerializer):
    created = FormattedDateTimeField(read_only=True)
    updated = FormattedDateTimeField(read_only=True)
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
            "primary_image",
            "user",
            "approved",
            "created",
            "updated",
        ]

        read_only_fields = ["id", "slug", "created", "updated", "user", "approved"]
        write_only_fields = ["category",]


    
    def create(self, validated_data):
        if validated_data:
            validated_data["user"] = self.context.get('request').user
            product = MarketPlaceProduct.objects.create(**validated_data)
        return product
    
    def update(self, instance, validated_data):
        instance.name = validated_data.get('name', instance.name)
        instance.description = validated_data.get('description', instance.description)
        instance.price = validated_data.get('price', instance.price)
        instance.category = validated_data.get('category', instance.category)
        instance.quantity = validated_data.get('quantity', instance.quantity)
        instance.size = validated_data.get('size', instance.size)
        instance.colour = validated_data.get('colour', instance.colour)
        instance.tags = validated_data.get('tags', instance.tags)
        instance.stock_status = validated_data.get('stock_status', instance.stock_status)
        if 'primary_image' in validated_data:
            instance.primary_image = validated_data['primary_image']
        instance.save()
        return super().update(instance, validated_data)

class TakaProductSerializer(serializers.ModelSerializer):
    created = FormattedDateTimeField(read_only=True)
    updated = FormattedDateTimeField(read_only=True)
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
            "primary_image",
            "user",
            "approved",
            "created",
            "updated",
        ]

        read_only_fields = ["id", "slug", "created", "updated", "user", "approved"]
        write_only_fields = ["category",]

    
    def create(self, validated_data):
        if validated_data:
            validated_data["service_provider"] = self.context.get('request').user
            product = TakaProduct.objects.create(**validated_data)
        return product
    
    def update(self, instance, validated_data):
        instance.name = validated_data.get('name', instance.name)
        instance.description = validated_data.get('description', instance.description)
        instance.price = validated_data.get('price', instance.price)
        instance.category = validated_data.get('category', instance.category)
        instance.quantity = validated_data.get('quantity', instance.quantity)
        instance.size = validated_data.get('size', instance.size)
        instance.colour = validated_data.get('colour', instance.colour)
        instance.tags = validated_data.get('tags', instance.tags)
        instance.stock_status = validated_data.get('stock_status', instance.stock_status)
        if 'primary_image' in validated_data:
            instance.primary_image = validated_data['primary_image']
        instance.save()
        return super().update(instance, validated_data)

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
    image = serializers.ImageField(required=True)
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
