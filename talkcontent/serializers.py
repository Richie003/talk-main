from .models import News, NewsImage, Event, PostContent, PostImages, PostVideos, PostLikes, PostComments, SharePost, RePostContent
from rest_framework import serializers
from utils.helpers import FormattedDateTimeField


class EventSerializer(serializers.ModelSerializer):
    class Meta:
        model = Event
        fields = ['id', 'user', 'event_name', 'event_image', 'event_date', 'event_fees', 'created', 'updated']
        read_only_fields = ['id', 'user', 'created', 'updated']


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

class PostContentImageSerializer(serializers.ModelSerializer):
    created = FormattedDateTimeField(read_only=True)
    updated = FormattedDateTimeField(read_only=True)

    class Meta:
        model = PostImages
        fields = [
            "id",
            "post",
            "image",
            "created",
            "updated"
        ]
        read_only_fields = ["id", "created", "updated", "post"]
        extra_kwargs = {
            'image': {'required': True}
        }
    
    def create(self, validated_data):
        return PostContent.objects.create(**validated_data)

class PostContentSerializer(serializers.ModelSerializer):
    created = FormattedDateTimeField(read_only=True)
    updated = FormattedDateTimeField(read_only=True)
    images = PostContentImageSerializer(source="post_images", many=True, read_only=True)
    upload_images = serializers.ListField(child=serializers.FileField(allow_empty_file=True), write_only=True)
    tags = serializers.ListField(child=serializers.CharField(max_length=50), required=False)

    class Meta:
        model = PostContent
        fields = [
            'id', 
            'user',
            'title', 
            'content', 
            'images', 
            'upload_images',
            'tags', 
            # 'likes', 
            'is_sponsored',
            'is_flagged',
            'is_reported', 
            'created', 
            'updated'
        ]

        read_only_fields = ['id', 'user', 'created', 'updated', 'is_flagged', 'is_reported']
        extra_kwargs = {
            'upload_images': {'required': True}
        }

    def create(self, validated_data):
        images = validated_data.pop("upload_images", [])
        post = PostContent.objects.create(user=self.context["request"].user, **validated_data)
        for img in images:
            PostImages.objects.create(post=post, image=img)
        return post

class PostLikesSerializer(serializers.ModelSerializer):
    class Meta:
        model = PostLikes
        fields = [
            "post",
            "likes"
        ]
        read_only_fields = ["likes",]


class PostCommentsSerializer(serializers.ModelSerializer):
    parent_comment = serializers.PrimaryKeyRelatedField(queryset=PostComments.objects.all(), required=False, allow_null=True)
    class Meta:
        model = PostComments
        fields = [
            "id",
            "post",
            "commented_by",
            "comment",
            "parent_comment"
        ]
        read_only_fields = ["id", "commented_by",]

class RePostContentSerializer(serializers.ModelSerializer):
    class Meta:
        model=RePostContent
        fields=[
            "user",
            "original_post",
            "additional_content"
        ]
        read_only_fields = ["user",]

    def create(self, validated_data):
        return RePostContent.objects.create(**validated_data)

class SharePostSerializer(serializers.ModelSerializer):
    class Meta:
        model = SharePost
        fields = [
            "post",
            "shared_by",
            "shared_with"
        ]
        read_only_fields = ["shared_by", "shared_with"]
