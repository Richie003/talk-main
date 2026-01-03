from django.db import models
from django.conf import settings
from django.utils import timezone
from django.dispatch import receiver
from django.db.models.signals import post_save, post_delete
from utils.custom_enums import MessageType

# Assumes ModelUtilsMixin defines `created` and `updated` timestamps and common helpers
from utils.models import ModelUtilsMixin
from utils.custom_enums import ParticipantRole

User = settings.AUTH_USER_MODEL


def upload_to_instance_slug(instance, filename):
    # store attachments under conversation id to make it easy to list for backups
    conv_id = getattr(instance.conversation, "id", "unassigned")
    return f"chat_attachments/{conv_id}/{filename}"


class Conversation(ModelUtilsMixin):
    ONE_TO_ONE = "one_to_one"
    GROUP = "group"
    TYPE_CHOICES = [
        (ONE_TO_ONE, "One to One"),
        (GROUP, "Group"),
    ]

    type = models.CharField(max_length=20, choices=TYPE_CHOICES, default=ONE_TO_ONE)

    # Denormalized fields to speed up reads
    title = models.CharField(max_length=255, blank=True, null=True)
    metadata = models.JSONField(blank=True, null=True)

    # Denormalized pointer to the latest message to avoid expensive queries
    last_message = models.ForeignKey(
        "Message",
        related_name="+",
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
    )

    last_activity = models.DateTimeField(blank=True, null=True)

    class Meta:
        indexes = [
            models.Index(fields=["created"]),
            models.Index(fields=["type"]),
        ]

    def __str__(self):
        return f"Conversation {self.id} ({self.type})"


class Participant(ModelUtilsMixin):
    conversation = models.ForeignKey(Conversation, related_name="participants", on_delete=models.CASCADE)
    user = models.ForeignKey(User, related_name="chat_participations", on_delete=models.CASCADE)

    # role enum from your utils
    role = models.CharField(max_length=50, default=ParticipantRole.MEMBER[0], choices=ParticipantRole.choices())

    joined_at = models.DateTimeField(default=timezone.now)
    left_at = models.DateTimeField(blank=True, null=True)

    # per-user denormalized values that change often and are read a lot
    last_read_at = models.DateTimeField(blank=True, null=True)
    unread_count = models.PositiveIntegerField(default=0)

    class Meta:
        unique_together = (("conversation", "user"),)
        indexes = [models.Index(fields=["conversation", "user"])]

    def __str__(self):
        return f"{self.user} in conv {self.conversation.id}"



class Message(ModelUtilsMixin):
    conversation = models.ForeignKey(Conversation, related_name="messages", on_delete=models.CASCADE)
    sender = models.ForeignKey(User, related_name="sent_messages", on_delete=models.SET_NULL, null=True)

    # message core
    body = models.TextField(blank=True, null=True)
    message_type = models.CharField(max_length=20, choices=MessageType.choices(), default=MessageType.TEXT[0])

    # keep attachments in a separate table (FileAttachment)
    metadata = models.JSONField(default=dict, blank=True, null=True)

    # soft delete fields
    is_deleted = models.BooleanField(default=False)
    deleted_at = models.DateTimeField(blank=True, null=True)

    class Meta:
        indexes = [
            models.Index(fields=["conversation", "created"]),
        ]

    def mark_deleted(self):
        self.is_deleted = True
        self.deleted_at = timezone.now()
        self.save(update_fields=["is_deleted", "deleted_at"])

    def __str__(self):
        return f"Message {self.id} in conv {self.conversation_id}"


class FileAttachment(ModelUtilsMixin):
    # One attachment per file row, linked to a message
    message = models.ForeignKey(Message, related_name="file_attachments", on_delete=models.CASCADE)

    # prefer FileField (backed by S3/GCS in production); keep `url` for externally hosted files
    file = models.FileField(upload_to=upload_to_instance_slug, blank=True, null=True)
    external_url = models.URLField(blank=True, null=True)

    # helpful metadata
    content_type = models.CharField(max_length=255, blank=True, null=True)
    size = models.PositiveIntegerField(blank=True, null=True)

    class Meta:
        indexes = [models.Index(fields=["message"])]

    def __str__(self):
        return f"FileAttachment {self.id} for msg {self.message_id}"


class ReadReceipt(ModelUtilsMixin):
    message = models.ForeignKey(Message, related_name="read_receipts", on_delete=models.CASCADE)
    user = models.ForeignKey(User, related_name="read_receipts", on_delete=models.CASCADE)
    read_at = models.DateTimeField()

    class Meta:
        unique_together = (("message", "user"),)
        indexes = [models.Index(fields=["message", "user"])]

    def __str__(self):
        return f"ReadReceipt msg:{self.message_id} user:{self.user_id}"


# -------------------------
# Signals to keep denormalized fields in sync
# -------------------------

@receiver(post_save, sender=Message)
def update_conversation_on_new_message(sender, instance: Message, created, **kwargs):
    # update conversation.last_message and last_activity
    conv = instance.conversation
    if created and not instance.is_deleted:
        Conversation.objects.filter(pk=conv.pk).update(last_message=instance, last_activity=instance.created)

        # increment unread_count for participants except the sender
        Participant.objects.filter(conversation=conv).exclude(user=instance.sender).update(unread_count=models.F("unread_count") + 1)


@receiver(post_delete, sender=Message)
def handle_message_delete(sender, instance: Message, **kwargs):
    # If the deleted message was the conversation's last_message, clear or set to latest
    conv = instance.conversation
    if conv.last_message_id == instance.id:
        latest = conv.messages.filter(is_deleted=False).order_by("-created").first()
        conv.last_message = latest
        conv.last_activity = latest.created if latest else None
        conv.save(update_fields=["last_message", "last_activity"])
