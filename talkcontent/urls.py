from django.urls import path, include
from .views import (
    EventCreateAPIView, EventListAPIView, 
    EventUpdateAPIView, EventDeleteAPIView,
    CreatePostContentView, RetrievePostContentView,
    RetrieveDetailedPostContent, DeletePostContentView,
    UpdatePostContentView
)

# Events
events_urlpatterns = [
    path('', EventListAPIView.as_view(), name='event-list'),
    path('create/', EventCreateAPIView.as_view(), name='event-create'),
    path("update/<uuid:pk>/",
         EventUpdateAPIView.as_view(), name="event-update"),
    path('delete/<uuid:pk>/',
         EventDeleteAPIView.as_view(), name='event-delete'),
]
# Post
post_urlpatterns = [
    path('create/', CreatePostContentView.as_view()),
    path('update/<str:pk>/', UpdatePostContentView.as_view()),
    path('delete/<str:pk>/', DeletePostContentView.as_view()),
    path('retrieve/', RetrievePostContentView.as_view()),
    path('retrieve/<str:pk>/', RetrieveDetailedPostContent.as_view()),
]
urlpatterns = [
    path("events/", include(events_urlpatterns)),
    path("post/", include(post_urlpatterns))
]
