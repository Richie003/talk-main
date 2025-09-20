from django.urls import path, include
from .views import (
    EventCreateAPIView, EventListAPIView, 
    EventUpdateAPIView, EventDeleteAPIView,
    CreatePostContentView, RetrievePostContentView,
    RetrieveDetailedPostContent, DeletePostContentView,
    UpdatePostContentView, LikePostContentView,
    CommentPostContentView, RetrievePostCommentsView
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
    path('retrieve/<str:post_id>/', RetrieveDetailedPostContent.as_view()),
    path('like/', LikePostContentView.as_view()),
    path('comment/', CommentPostContentView.as_view()),
    path('get-comments/<str:post_id>/', RetrievePostCommentsView.as_view()),
    # path('share/', SharePostContentView.as_view()),
]
urlpatterns = [
    path("events/", include(events_urlpatterns)),
    path("post/", include(post_urlpatterns))
]
