from django.urls import path
from .views import EventCreateAPIView, EventListAPIView

urlpatterns = [
    path('create/', EventCreateAPIView.as_view(), name='event-create'),
    path('list/', EventListAPIView.as_view(), name='event-list'),
]
