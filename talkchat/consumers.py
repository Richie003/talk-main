from channels.generic.websocket import AsyncJsonWebsocketConsumer
from channels.db import database_sync_to_async
from django.contrib.auth import get_user_model
from django.shortcuts import get_object_or_404

from .models import Conversation, Participant, Message
from .serializers import MessageSerializer
from datetime import timezone

User = get_user_model()


class ChatConsumer(AsyncJsonWebsocketConsumer):
    async def connect(self):
        # expects query params: ?conversation_id=<id>
        self.conversation_id = self.scope["url_route"]["kwargs"].get("conversation_id")
        if not self.conversation_id:
            await self.close()
            return

        # check membership
        is_participant = await database_sync_to_async(self._is_participant)()
        if not is_participant:
            await self.close()
            return

        self.room_group_name = f"chat_{self.conversation_id}"
        await self.channel_layer.group_add(self.room_group_name, self.channel_name)
        await self.accept()

    @database_sync_to_async
    def _is_participant(self):
        conv = get_object_or_404(Conversation, pk=self.conversation_id)
        return conv.participants.filter(user=self.scope["user"], left_at__isnull=True).exists()

    async def disconnect(self, code):
        await self.channel_layer.group_discard(self.room_group_name, self.channel_name)

    async def receive_json(self, content):
        # expect {"type": "message.create", "body": "..."}
        msg_type = content.get("type")
        if msg_type == "message.create":
            body = content.get("body")
            message = await database_sync_to_async(self._create_message)(body)
            serialized = MessageSerializer(message).data
            # broadcast
            await self.channel_layer.group_send(self.room_group_name, {
                "type": "chat.message",
                "message": serialized,
            })

        elif msg_type == "message.read":
            message_id = content.get("message_id")
            await database_sync_to_async(self._mark_read)(message_id)

    def _create_message(self, body):
        conv = Conversation.objects.get(pk=self.conversation_id)
        msg = Message.objects.create(conversation=conv, sender=self.scope["user"], body=body)
        return msg

    def _mark_read(self, message_id):
        # update participant last_read_at and unread_count
        try:
            message = Message.objects.get(pk=message_id)
            part = Participant.objects.get(conversation=message.conversation, user=self.scope["user"])
            part.last_read_at = timezone.now()
            part.unread_count = 0
            part.save(update_fields=["last_read_at", "unread_count"])
        except Exception:
            pass

    async def chat_message(self, event):
        # event from group_send
        await self.send_json({"type": "message.received", "message": event["message"]})