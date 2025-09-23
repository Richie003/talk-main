from django.db import models
from utils.models import ModelUtilsMixin
from django.utils.translation import gettext_lazy as _
from django.conf import settings
from django.utils import timezone
from django.utils.text import slugify
from polymorphic.models import PolymorphicModel
from polymorphic.managers import PolymorphicManager

user = settings.AUTH_USER_MODEL

def post_image_upload_path(instance, filename):
    return f"post/imgs/{instance.post.user.talk_id}/{slugify(instance.post.title)}-{filename}"

def post_video_upload_path(instance, filename):
    return f"post/vids/{instance.post.user.talk_id}/{slugify(instance.post.title)}-{filename}"


class Tags(models.TextChoices):
    GENERAL = "general", "General" 
    EVENT = "event", "Event"
    JOB = "job", "Job"
    ANNOUNCEMENT = "announcement", "Announcement"
    DISCUSSION = "discussion", "Discussion"
    PROMOTION = "promotion", "Promotion"

class CommonFields(models.Model):
    user = models.ForeignKey(user, on_delete=models.CASCADE, null=True)
    is_reported = models.BooleanField(default=False)
    is_flagged = models.BooleanField(default=False)

    class Meta:
        abstract = True

class PostContent(PolymorphicModel, ModelUtilsMixin, CommonFields):
    objects = PolymorphicManager()
    title = models.CharField(max_length=500)
    slug = models.SlugField(unique=True, null=False, blank=True)
    summary = models.TextField(null=True, blank=True)
    content = models.TextField(null=True, blank=True)
    tags = models.JSONField(null=True, blank=True)
    is_sponsored = models.BooleanField(default=False)

    class Meta:
        ordering = ["-created", "-updated"]

    def __str__(self):
        return str(self.title)
    
    def post_profile(self):
        likes = self.get_likes() if hasattr(self, 'post_likes') else []
        return {
            "id": self.id,
            "title": self.title,
            "slug": self.slug,
            "summary": self.summary,
            "content": self.content,
            "tags": self.tags,
            "liked_by": likes,
            "comment_count": self.comments_count(),
            "like_count": len(likes),
            "images": self.get_images() if self.post_images.exists() else None,
            "videos": self.get_videos() if hasattr(self, 'post_videos') and self.post_videos.exists() else None,
            "created_by": f"{self.user.first_name} {self.user.last_name}",
            "created": self.created.strftime("%Y-%m-%d %H:%M:%S"),
            "updated": self.updated.strftime("%Y-%m-%d %H:%M:%S"),
            # "is_repost": False
        }

    def save(self, *args, **kwargs):
        # Save first to get ID if it doesn't exist
        if not self.id:
            super().save(*args, **kwargs)
        if not self.slug:
            self.slug = f"{slugify(self.title)}-{self.id}"
        super().save(*args, **kwargs)

    def comments_count(self):
        return self.post_comments.count()

    def get_likes(self):
        likes = self.post_likes.get_likes()
        return likes if likes else []

    def get_images(self):
        return [image.image.url for image in self.post_images.all() if image.image]
    
    def get_videos(self):
        return [video.video.url for video in self.post_videos.all() if video.video]

class RePostContent(PostContent):
    original_post = models.ForeignKey(
        PostContent,
        on_delete=models.CASCADE,
        related_name="reposts",
        null=True,
        blank=True,
        limit_choices_to={"repostcontent__isnull": True}
    )
    additional_content = models.TextField(null=True, blank=True)

    def save(self, *args, **kwargs):
        if not self.id:
            super().save(*args, **kwargs)

        # Generate slug if missing
        if not self.slug:
            self.slug = f"{slugify(self.title or 'repost')}-{self.id}"
        
        super().save(*args, **kwargs)

    def post_profile(self):
            """
            Returns the feed-friendly representation of the repost.
            """
            if not self.original_post:
                return {
                    "id": self.id,
                    "is_repost": True,
                    "reposted_by": f"{self.user.first_name} {self.user.last_name}",
                    "repost_note": self.additional_content,
                    "repost_date": self.created.strftime("%Y-%m-%d %H:%M:%S"),
                    "original_post": None,
                }

            return {
                "id": self.id,
                "is_repost": True,
                "reposted_by": f"{self.user.first_name} {self.user.last_name}",
                "repost_note": self.additional_content,
                "repost_date": self.created.strftime("%Y-%m-%d %H:%M:%S"),
                "original_post": self.original_post.post_profile(),
            }


class PostLikes(ModelUtilsMixin):
    post = models.OneToOneField(PostContent, on_delete=models.CASCADE, related_name="post_likes")
    likes = models.ManyToManyField(user, blank=True, related_name="liked_posts")

    def __str__(self):
        return f"Likes for {self.post.title}"

    def add_like(self, user_obj):
        self.likes.add(user_obj)

    def remove_like(self, user_obj):
        self.likes.remove(user_obj)

    def get_likes(self):
        return [
            {
                "id": u.id,
                "full_name": f"{u.first_name} {u.last_name}".strip()
            }
            for u in self.likes.all()
        ]

class PostComments(ModelUtilsMixin):
    post = models.ForeignKey(PostContent, on_delete=models.CASCADE, related_name="post_comments")
    commented_by = models.ForeignKey(user, on_delete=models.CASCADE, related_name="comments_made")
    comment = models.TextField()
    parent_comment = models.ForeignKey('self', null=True, blank=True, on_delete=models.CASCADE, related_name="replies")

    def __str__(self):
        return f"Comment by {self.commented_by.talk_id} on {self.post.title}"
    

class PostImages(ModelUtilsMixin):
    post = models.ForeignKey(PostContent, on_delete=models.CASCADE, related_name="post_images")
    image = models.ImageField(upload_to=post_image_upload_path, null=True, blank=True)

    def __str__(self):
        return str(self.image)
    
class PostVideos(ModelUtilsMixin):
    post = models.ForeignKey(PostContent, on_delete=models.CASCADE, related_name="post_videos")
    video = models.FileField(upload_to=post_video_upload_path, null=True, blank=True)

    def __str__(self):
        return str(self.video)

class SharePost(ModelUtilsMixin):
    post = models.ForeignKey(PostContent, on_delete=models.CASCADE, related_name="shared_posts")
    shared_by = models.ForeignKey(user, on_delete=models.CASCADE, related_name="posts_shared")
    shared_with = models.ManyToManyField(user, related_name="posts_received")

    def __str__(self):
        return f"{self.post.title} shared by {self.shared_by.talk_id}"

class Event(ModelUtilsMixin, CommonFields):
    event_name = models.CharField(max_length=255)
    event_image = models.ImageField(upload_to="")
    event_date = models.DateTimeField(default=timezone.now)
    event_fees = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    
    def __str__(self):
        return str(self.event_name)
    
class News(ModelUtilsMixin, CommonFields):
    title = models.CharField(max_length=255, default="", blank=False)
    slug = models.SlugField(unique=True, null=False, blank=True)
    body = models.TextField(default="", blank=False)

    def __str__(self):
        return f"{self.title} - {self.body[:20]}..."
    
    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = f"{slugify(self.title)}-{self.id}"
        super().save(*args, **kwargs)

class NewsImage(ModelUtilsMixin):
    news = models.ForeignKey(News, on_delete=models.CASCADE, related_name="images")
    image = models.ImageField(upload_to="news_images/")

    def __str__(self):
        return f"Image for {self.news.title}"
