from rest_framework import generics
from rest_framework import status, generics
from rest_framework.response import Response
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi
from .models import Event
from .serializers import EventSerializer

# =========================
# EVENTS VIEWS
# =========================


class EventCreateAPIView(generics.CreateAPIView):
    queryset = Event.objects.all()
    serializer_class = EventSerializer

    @swagger_auto_schema(request_body=EventSerializer, responses={201: EventSerializer})
    def post(self, request, *args, **kwargs):
        return super().post(request, *args, **kwargs)


class EventListAPIView(generics.ListAPIView):
    queryset = Event.objects.all()
    serializer_class = EventSerializer


class EventUpdateAPIView(generics.UpdateAPIView):
    queryset = Event.objects.all()
    serializer_class = EventSerializer
    lookup_field = "pk"
    http_method_names = ['patch']

    @swagger_auto_schema(
        request_body=EventSerializer,
        responses={200: EventSerializer}
    )
    def put(self, request, *args, **kwargs):
        return super().put(request, *args, **kwargs)

    @swagger_auto_schema(
        request_body=EventSerializer,
        responses={200: EventSerializer}
    )
    def patch(self, request, *args, **kwargs):
        return super().patch(request, *args, **kwargs)


class EventDeleteAPIView(generics.DestroyAPIView):
    queryset = Event.objects.all()
    serializer_class = EventSerializer
    lookup_field = "pk"

    @swagger_auto_schema(
        responses={204: "Event deleted successfully"}
    )
    def delete(self, request, *args, **kwargs):
        return super().delete(request, *args, **kwargs)
