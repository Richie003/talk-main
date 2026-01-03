from rest_framework import viewsets, permissions, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.parsers import MultiPartParser, FormParser
from django.shortcuts import get_object_or_404
from drf_spectacular.utils import extend_schema_view, extend_schema

from .models import Conversation, Participant, Message, FileAttachment
from .serializers import (
    ConversationSerializer, ParticipantSerializer, MessageSerializer, FileAttachmentSerializer, ReadReceiptSerializer
)


class IsConversationParticipant(permissions.BasePermission):
    """Allow access only to participants of the conversation."""

    def has_object_permission(self, request, view, obj):
        return obj.participants.filter(user=request.user, left_at__isnull=True).exists()

@extend_schema_view(
    list=extend_schema(summary="List Conversations", tags=["chat conversation"], operation_id="list_conversations"),
    retrieve=extend_schema(summary="Retrieve a Conversation", tags=["chat conversation"], operation_id="retrieve_conversation"),
    create=extend_schema(summary="Create a Conversation", tags=["chat conversation"], operation_id="create_conversation"),
    update=extend_schema(summary="Update a Conversation", tags=["chat conversation"], operation_id="update_conversation"),
    partial_update=extend_schema(summary="Partially Update a Conversation", tags=["chat conversation"], operation_id="partial_update_conversation"),
    destroy=extend_schema(summary="Delete a Conversation", tags=["chat conversation"], operation_id="delete_conversation"),
)
class ConversationViewSet(viewsets.ModelViewSet):
    queryset = Conversation.objects.all().prefetch_related("participants", "messages")
    serializer_class = ConversationSerializer
    permission_classes = [permissions.IsAuthenticated]
    http_method_names = ["get", "post", "patch", "delete"]

    @extend_schema(summary="Add Participant to Conversation", tags=["chat"], operation_id="add_participant")
    @action(detail=True, methods=["post"], url_path="add-participant")
    def add_participant(self, request, pk=None):
        conv = self.get_object()
        serializer = ParticipantSerializer(data={**request.data, "conversation": conv.id})
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)


@extend_schema_view(
    list=extend_schema(summary="List Participants", tags=["chat participant"], operation_id="list_participants"),
    retrieve=extend_schema(summary="Retrieve a Participant", tags=["chat participant"], operation_id="retrieve_participant"),
    create=extend_schema(summary="Create a Participant", tags=["chat participant"], operation_id="create_participant"),
    update=extend_schema(summary="Update a Participant", tags=["chat participant"], operation_id="update_participant"),
    partial_update=extend_schema(summary="Partially Update a Participant", tags=["chat participant"], operation_id="partial_update_participant"),
    destroy=extend_schema(summary="Delete a Participant", tags=["chat participant"], operation_id="delete_participant"),
)
class ParticipantViewSet(viewsets.ModelViewSet):
    queryset = Participant.objects.all()
    serializer_class = ParticipantSerializer
    permission_classes = [permissions.IsAuthenticated]
    http_method_names = ["get", "post", "patch", "delete"]


@extend_schema_view(
    list=extend_schema(summary="List Messages", tags=["chat message"], operation_id="list_messages"),
    retrieve=extend_schema(summary="Retrieve a Message", tags=["chat message"], operation_id="retrieve_message"),
    create=extend_schema(summary="Create a Message", tags=["chat message"], operation_id="create_message"),
    update=extend_schema(summary="Update a Message", tags=["chat message"], operation_id="update_message"),
    partial_update=extend_schema(summary="Partially Update a Message", tags=["chat message"], operation_id="partial_update_message"),
    destroy=extend_schema(summary="Delete a Message", tags=["chat message"], operation_id="delete_message"),
)
class MessageViewSet(viewsets.ModelViewSet):
    queryset = Message.objects.all().select_related("conversation", "sender").prefetch_related("file_attachments")
    serializer_class = MessageSerializer
    permission_classes = [permissions.IsAuthenticated]
    parser_classes = (MultiPartParser, FormParser)
    http_method_names = ["get", "post", "patch", "delete"]

    def perform_create(self, serializer):
        # attach sender automatically
        msg = serializer.save(sender=self.request.user)
        # update conversation.last_message via signal will handle denormalization
        return msg

    @extend_schema(summary="Upload Attachment to Message", tags=["chat"], operation_id="upload_attachment")
    @action(detail=True, methods=["post"])
    def upload_attachment(self, request, pk=None):
        message = self.get_object()
        serializer = FileAttachmentSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save(message=message)
        return Response(serializer.data, status=status.HTTP_201_CREATED)


@extend_schema_view(
    list=extend_schema(summary="List File Attachments", tags=["chat file attachment"], operation_id="list_file_attachments"),
    retrieve=extend_schema(summary="Retrieve a File Attachment", tags=["chat file attachment"], operation_id="retrieve_file_attachment"),
    create=extend_schema(summary="Create a File Attachment", tags=["chat file attachment"], operation_id="create_file_attachment"),
    update=extend_schema(summary="Update a File Attachment", tags=["chat file attachment"], operation_id="update_file_attachment"),
    partial_update=extend_schema(summary="Partially Update a File Attachment", tags=["chat file attachment"], operation_id="partial_update_file_attachment"),
    destroy=extend_schema(summary="Delete a File Attachment", tags=["chat file attachment"], operation_id="delete_file_attachment"),
)
class FileAttachmentViewSet(viewsets.ModelViewSet):
    queryset = FileAttachment.objects.all()
    serializer_class = FileAttachmentSerializer
    permission_classes = [permissions.IsAuthenticated]
    parser_classes = (MultiPartParser, FormParser)
    http_method_names = ["get", "post", "patch", "delete"]

