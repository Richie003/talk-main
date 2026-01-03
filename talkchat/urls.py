from django.urls import path, include
from rest_framework.routers import DefaultRouter

from .views import (
    ConversationViewSet,
    ParticipantViewSet,
    MessageViewSet,
    FileAttachmentViewSet,
)

router = DefaultRouter()
router.register(r"conversations", ConversationViewSet, basename="conversation")
router.register(r"participants", ParticipantViewSet, basename="participant")
router.register(r"messages", MessageViewSet, basename="message")
router.register(r"attachments", FileAttachmentViewSet, basename="attachment")

urlpatterns = [
    path("chat/", include(router.urls)),
]
