from django.db import models
from utils.models import ModelUtilsMixin
from django.utils.translation import gettext_lazy as _
from django.conf import settings
from django.utils import timezone
from django.utils.text import slugify
from .schemas import CollegeCourses

user = settings.AUTH_USER_MODEL


class Tags(models.TextChoices):
    GENERAL = "general", "General" 
    EVENT = "event", "Event"
    JOB = "job", "Job"
    ANNOUNCEMENT = "announcement", "Announcement"
    DISCUSSION = "discussion", "Discussion"
    PROMOTION = "promotion", "Promotion"


class PostContent(ModelUtilsMixin, CollegeCourses):
    user_id = models.ForeignKey(user, on_delete=models.CASCADE, related_name="post_user")
    title = models.CharField(max_length=500)
    summary = models.TextField(null=True, blank=True)
    content = models.TextField(null=True, blank=True)
    url = models.URLField(unique=True)
    image_url = models.URLField(null=True, blank=True)
    tags = models.JSONField(null=True, blank=True)
    likes = models.ManyToManyField(user, blank=True, related_name="liked_posts")
    share_to_group = models.JSONField(default=CollegeCourses.get_courses_offered)
    is_reported = models.BooleanField(default=False)
    is_flagged = models.BooleanField(default=False)
    is_sponsored = models.BooleanField(default=False)

    def __str__(self):
        return str(self.title)

class CommonFields(models.Model):
    user = models.ForeignKey(user, on_delete=models.CASCADE)
    is_reported = models.BooleanField(default=False)
    is_flagged = models.BooleanField(default=False)

    class Meta:
        abstract = True


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