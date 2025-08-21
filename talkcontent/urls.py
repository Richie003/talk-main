from django.urls import path
from .views import (
    EventCreateAPIView, EventListAPIView, EventUpdateAPIView, EventDeleteAPIView,
)

# Events
urlpatterns = [
    path('events/', EventListAPIView.as_view(), name='event-list'),
    path('events/create/', EventCreateAPIView.as_view(), name='event-create'),
    path("events/update/<uuid:pk>/",
         EventUpdateAPIView.as_view(), name="event-update"),
    path('events/delete/<uuid:pk>/',
         EventDeleteAPIView.as_view(), name='event-delete'),
]
