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
    Category,
    SavedItem
)
from utils.helpers import FormattedDateTimeField

class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = ['id', 'name']
        read_only_fields = ['id']
        extra_kwargs = {
            'name': {'required': True}
        }
        def create(self, validated_data):
            return Category.objects.create(**validated_data)
        def update(self, instance, validated_data):
            instance.name = validated_data.get('name', instance.name)
            instance.save()
            return instance
        def delete(self, instance):
            instance.delete()
            return instance
        def get(self, instance):
            return Category.objects.all()

class MarketPlaceProductSerializer(serializers.ModelSerializer):
    created = FormattedDateTimeField(read_only=True)
    updated = FormattedDateTimeField(read_only=True)
    category = serializers.ChoiceField(
        choices=Category.objects.values_list('name', 'id'),
        write_only=True,
        help_text="Select a category by name"
    )
    class Meta:
        model = MarketPlaceProduct
        fields = [
            "id",
            "name",
            "slug",
            "description",
            "category",
            "price",
            "address",
            "negotiable",
            "primary_image",
            "user",
            "approved",
            "created",
            "updated",
        ]

        read_only_fields = ["id", "slug", "created", "updated", "user", "approved"]
        write_only_fields = ["category",]

    def validate_category(self, value):
        """
        Convert the category name to its corresponding UUID.
        """
        try:
            category = Category.objects.get(name=value)
            return category.id  # Replace with `category.uuid` if UUID is used
        except Category.DoesNotExist:
            raise serializers.ValidationError(f"Category '{value}' does not exist.")

    
    def create(self, validated_data):
        if validated_data:
            validated_data["service_provider"] = self.context.get('request').user
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
    category = serializers.ChoiceField(
        choices=Category.objects.values_list('name', 'id'),
        write_only=True,
        help_text="Select a category by name"
    )
    class Meta:
        model = TakaProduct
        fields = [
            "id",
            "name",
            "slug",
            "description",
            "category",
            "price",
            "address",
            "negotiable",
            "primary_image",
            "user",
            "approved",
            "created",
            "updated",
        ]

        read_only_fields = ["id", "slug", "created", "updated", "user", "approved"]
        write_only_fields = ["category",]

    def validate_category(self, value):
        """
        Convert the category name to its corresponding UUID.
        """
        try:
            category = Category.objects.get(name=value)
            return category.id  # Replace with `category.uuid` if UUID is used
        except Category.DoesNotExist:
            raise serializers.ValidationError(f"Category '{value}' does not exist.")

    
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
