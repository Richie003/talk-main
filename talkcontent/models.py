from django.db import models
from utils.models import ModelUtilsMixin
from django.utils.translation import gettext_lazy as _
from django.conf import settings
from django.utils import timezone
from django.utils.text import slugify
from .schemas import CollegeCourses

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

class PostContent(ModelUtilsMixin, CommonFields):
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
        return {
            "title": self.title,
            "slug": self.slug,
            "summary": self.summary,
            "content": self.content,
            "tags": self.tags,
            "liked_by": self.liked_by(),
            "like_count": self.like_count(),
            "images": self.get_images(),
            "videos": self.get_videos(),
            "created_by": str(self.user.first_name) + " " + str(self.user.last_name),
            "created": self.created.strftime("%Y-%m-%d %H:%M:%S"),
            "updated": self.updated.strftime("%Y-%m-%d %H:%M:%S"),
        }
    
    def save(self, *args, **kwargs):
        if not self.slug and self.id:
            self.slug = f"{slugify(self.title)}-{self.id}"
        super().save(*args, **kwargs)
    
    def liked_by(self):
        user = [user.email for user in self.post_likes.all()]
        return user
    
    def like_count(self):
        return self.post_likes.count()

    def get_images(self):
        return [image.image.url for image in self.post_images.all() if image.image]

    def get_videos(self):
        return [video.video_path.url for video in self.post_videos.all() if video.video_path]

    # def get_reviews(self):
    #     return [review.comment for review in self.marketplace_reviews.all() if review.comment]
    
class PostLikes(ModelUtilsMixin):
    post = models.ForeignKey(PostContent, on_delete=models.CASCADE, related_name="post_likes")
    likes = models.ManyToManyField(user, blank=True, related_name="liked_posts")

    def __str__(self):
        return f"Likes for {self.post.title}"
    

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
