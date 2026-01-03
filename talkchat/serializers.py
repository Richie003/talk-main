from rest_framework import serializers
from .models import Conversation, Participant, Message, FileAttachment, ReadReceipt




class FileAttachmentSerializer(serializers.ModelSerializer):
    class Meta:
        model = FileAttachment
        fields = ("id", "file", "external_url", "content_type", "size", "created")
        read_only_fields = ("id", "created")




class MessageSerializer(serializers.ModelSerializer):
    file_attachments = FileAttachmentSerializer(many=True, read_only=True)
    sender = serializers.PrimaryKeyRelatedField(read_only=True)


    class Meta:
        model = Message
        fields = ("id", "conversation", "sender", "body", "message_type", "metadata", "is_deleted", "deleted_at", "created", "file_attachments")
        read_only_fields = ("id", "created", "deleted_at", "is_deleted")




class ParticipantSerializer(serializers.ModelSerializer):
    # user = serializers.PrimaryKeyRelatedField(queryset=__import__("django.conf").conf.settings.AUTH_USER_MODEL)


    class Meta:
        model = Participant
        fields = ("id", "conversation", "user", "role", "joined_at", "left_at", "last_read_at", "unread_count")
        read_only_fields = ("id", "joined_at")




class ConversationSerializer(serializers.ModelSerializer):
    participants = ParticipantSerializer(many=True, read_only=True)
    last_message = MessageSerializer(read_only=True)


    class Meta:
        model = Conversation
        fields = ("id", "type", "title", "metadata", "last_message", "last_activity", "participants", "created")
        read_only_fields = ("id", "last_message", "last_activity", "created")




class ReadReceiptSerializer(serializers.ModelSerializer):
    class Meta:
        model = ReadReceipt
        fields = ("id", "message", "user", "read_at")
        read_only_fields = ("id",)