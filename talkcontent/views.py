from rest_framework import status, generics
from rest_framework.response import Response
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi
from .models import Event
from .serializers import EventSerializer

tag_names = {
    "event": "Event",
}

# =========================
# EVENTS VIEWS
# =========================


class EventCreateAPIView(generics.CreateAPIView):
    queryset = Event.objects.all()
    serializer_class = EventSerializer

    @swagger_auto_schema(
        tags=[tag_names["event"]],
        operation_id="Create_Event",
        request_body=EventSerializer,
        responses={201: EventSerializer}
    )
    def post(self, request, *args, **kwargs):
        return super().post(request, *args, **kwargs)


class EventListAPIView(generics.ListAPIView):
    queryset = Event.objects.all()
    serializer_class = EventSerializer

    @swagger_auto_schema(
        tags=[tag_names["event"]],
        operation_id="List_Events",
        responses={200: EventSerializer(many=True)}
    )
    def get(self, request, *args, **kwargs):
        return super().get(request, *args, **kwargs)


class EventUpdateAPIView(generics.UpdateAPIView):
    queryset = Event.objects.all()
    serializer_class = EventSerializer
    lookup_field = "pk"
    http_method_names = ['patch']  # ✅ only PATCH

    @swagger_auto_schema(
        tags=[tag_names["event"]],
        operation_id="Update_Event",
        request_body=EventSerializer,
        responses={200: EventSerializer}
    )
    def patch(self, request, *args, **kwargs):
        return super().partial_update(request, *args, **kwargs)


class EventDeleteAPIView(generics.DestroyAPIView):
    queryset = Event.objects.all()
    serializer_class = EventSerializer
    lookup_field = "pk"

    @swagger_auto_schema(
        tags=[tag_names["event"]],
        operation_id="Delete_Event",
        responses={204: openapi.Response("Event deleted successfully")}
    )
    def delete(self, request, *args, **kwargs):
        instance = self.get_object()
        self.perform_destroy(instance)
        return Response(
            {"message": "Event deleted successfully"},
            status=status.HTTP_204_NO_CONTENT
        )
