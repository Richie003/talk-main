from rest_framework import status, generics
from rest_framework.response import Response
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi
from .models import Event
from .serializers import EventSerializer


class EventCreateAPIView(generics.CreateAPIView):
    queryset = Event.objects.all()
    serializer_class = EventSerializer

    @swagger_auto_schema(request_body=EventSerializer, responses={201: EventSerializer})
    def post(self, request, *args, **kwargs):
        return super().post(request, *args, **kwargs)


class EventListAPIView(generics.ListAPIView):
    queryset = Event.objects.all()
    serializer_class = EventSerializer
