# serializers.py

from .models import News, NewsImage
from rest_framework import serializers
from .models import Event


class EventSerializer(serializers.ModelSerializer):
    class Meta:
        model = Event
        fields = '__all__'


class NewsImageSerializer(serializers.ModelSerializer):
    class Meta:
        model = NewsImage
        fields = ['id', 'image']


class NewsSerializer(serializers.ModelSerializer):
    images = NewsImageSerializer(many=True, read_only=True)
    uploaded_images = serializers.ListField(
        child=serializers.ImageField(
            max_length=1000000, allow_empty_file=False, use_url=False),
        write_only=True
    )

    class Meta:
        model = News
        fields = ['id', 'title', 'body',
                  'created_at', 'images', 'uploaded_images']

    def validate_uploaded_images(self, value):
        if not value:
            raise serializers.ValidationError(
                "At least one image is required.")
        if len(value) > 10:
            raise serializers.ValidationError(
                "You cannot upload more than 10 images.")
        return value

    def create(self, validated_data):
        images = validated_data.pop('uploaded_images')
        news = News.objects.create(**validated_data)
        for image in images:
            NewsImage.objects.create(news=news, image=image)
        return news
