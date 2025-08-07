from django.db import models
from utils.models import ModelUtilsMixin
from django.utils.translation import gettext_lazy as _
from django.conf import settings
from django.utils import timezone
from .schemas import CollegeCourses

user = settings.AUTH_USER_MODEL


class MessageType(models.TextChoices):
    TEXT = "text", "Text"
    IMAGE = "image", "Image"
    VIDEO = "video", "Video"
    AUDIO = "audio", "Audio"
    FILE = "file", "File"


class Tags(models.TextChoices):
    GENERAL = "general", "General"
    EVENT = "event", "Event"
    JOB = "job", "Job"
    ANNOUNCEMENT = "announcement", "Announcement"
    DISCUSSION = "discussion", "Discussion"
    PROMOTION = "promotion", "Promotion"


class PostContent(ModelUtilsMixin, CollegeCourses):
    user_id = models.ForeignKey(
        user, on_delete=models.CASCADE, related_name="post_user")
    title = models.CharField(max_length=500)
    summary = models.TextField(null=True, blank=True)
    content = models.TextField(null=True, blank=True)
    url = models.URLField(unique=True)
    image_url = models.URLField(null=True, blank=True)
    tags = models.JSONField(null=True, blank=True)
    likes = models.ManyToManyField(
        user, blank=True, related_name="liked_posts")
    share_to_group = models.JSONField(
        default=CollegeCourses.get_courses_offered)
    is_reported = models.BooleanField(default=False)
    is_flagged = models.BooleanField(default=False)
    is_sponsored = models.BooleanField(default=False)

    def __str__(self):
        return str(self.title)


class Message(ModelUtilsMixin):
    sender = models.ForeignKey(
        user, on_delete=models.CASCADE, related_name='sent_messages')
    receiver = models.ForeignKey(
        user, on_delete=models.CASCADE, related_name='received_messages')
    message_type = models.CharField(
        max_length=20, choices=MessageType.choices, default=MessageType.TEXT)
    content = models.TextField()
    read = models.BooleanField(default=False)

    def __str__(self):
        return f"Message from {self.sender.user.username} to {self.receiver.user.username} at {self.timestamp}"


class Conversation(ModelUtilsMixin):
    participants = models.ManyToManyField(user)
    messages = models.ManyToManyField(Message, blank=True)

    def __str__(self):
        participants_str = ", ".join(
            [p.user.username for p in self.participants.all()])
        return f"Conversation between {participants_str}"


class GroupChat(ModelUtilsMixin):
    group_name = models.CharField(max_length=255)
    creator = models.ForeignKey(
        user, on_delete=models.CASCADE, related_name='created_groups')
    members = models.ManyToManyField(user, related_name='group_chats')
    messages = models.ManyToManyField(Message, blank=True)

    def __str__(self):
        return self.group_name


class Event(models.Model):
    event_name = models.CharField(max_length=255)
    event_image = models.ImageField(
        upload_to='events/images/', null=True, blank=True)
    event_date = models.DateTimeField()
    event_fees = models.DecimalField(
        max_digits=8, decimal_places=2, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.event_name
