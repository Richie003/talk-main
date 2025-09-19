from rest_framework import status, generics
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework.parsers import MultiPartParser, FormParser
from drf_spectacular.utils import extend_schema
from utils.helpers import custom_response
from .models import Event, PostContent
from .serializers import EventSerializer, PostContentSerializer, PostLikesSerializer

tag_names = {
    "event": "Event",
    "post": "Post",
}

# =========================
# EVENTS VIEWS
# =========================

class EventCreateAPIView(generics.CreateAPIView):
    queryset = Event.objects.all()
    serializer_class = EventSerializer
    permission_classes=[IsAuthenticated]

    @extend_schema(
        tags=[tag_names["event"]],
        operation_id="Create_Event"
    )
    def post(self, request, *args, **kwargs):
        return super().post(request, *args, **kwargs)

class EventListAPIView(generics.ListAPIView):
    queryset = Event.objects.all()
    serializer_class = EventSerializer

    @extend_schema(
        tags=[tag_names["event"]],
        operation_id="List_Events",
    )
    def get(self, request, *args, **kwargs):
        return super().get(request, *args, **kwargs)

class EventUpdateAPIView(generics.UpdateAPIView):
    queryset = Event.objects.all()
    serializer_class = EventSerializer
    lookup_field = "pk"
    http_method_names = ['patch']

    @extend_schema(
        tags=[tag_names["event"]],
        operation_id="Update_Event"
    )
    def patch(self, request, *args, **kwargs):
        return super().partial_update(request, *args, **kwargs)

class EventDeleteAPIView(generics.DestroyAPIView):
    queryset = Event.objects.all()
    serializer_class = EventSerializer
    lookup_field = "pk"

    @extend_schema(
        tags=[tag_names["event"]],
        operation_id="Delete_Event",
    )
    def delete(self, request, *args, **kwargs):
        instance = self.get_object()
        self.perform_destroy(instance)
        return Response(
            {"message": "Event deleted successfully"},
            status=status.HTTP_204_NO_CONTENT
        )

# =========================
# POSTS VIEWS
# =========================

class CreatePostContentView(generics.GenericAPIView):
    serializer_class=PostContentSerializer
    permission_classes=[IsAuthenticated]
    parser_classes=[MultiPartParser, FormParser]

    @extend_schema(tags=[tag_names['post']], operation_id="Create a Post")
    def post(self, request, *args, **kwargs):
        data = request.data
        print(data)
        serializer = self.get_serializer(data=data, context={"request": request})
        serializer.is_valid(raise_exception=True)
        serializer.save()

        return Response(
            custom_response(
                status_mthd=status.HTTP_201_CREATED,
                status="success",
                mssg="Post created successfully",
                data=serializer.data
            )
        )

class UpdatePostContentView(generics.UpdateAPIView):
    queryset = PostContent.objects.all()
    permission_classes=[IsAuthenticated]
    serializer_class = PostContentSerializer
    lookup_field = "pk"
    http_method_names = ['patch']
    parser_classes=[MultiPartParser, FormParser]

    @extend_schema(tags=[tag_names['post']], operation_id="Update a Post")
    def patch(self, request, *args, **kwargs):
        return super().partial_update(request, *args, **kwargs)

class RetrievePostContentView(generics.RetrieveAPIView):
    queryset = PostContent.objects.all()
    permission_classes=[IsAuthenticated]
    serializer_class = PostContentSerializer
    lookup_field = "pk"

    @extend_schema(tags=[tag_names['post']], operation_id="Retrieve all Post")
    def get(self, request, *args, **kwargs):
        posts = self.get_queryset()
        try:
            serializer = self.get_serializer(posts, many=True)
            data = serializer.data
            return Response(custom_response(
                status_mthd=status.HTTP_200_OK,
                status="success",
                mssg="Posts retrieved successfully",
                data=data
            ))
        except Exception as e:
            return Response(custom_response(
                status_mthd=status.HTTP_400_BAD_REQUEST,
                status="error",
                mssg=str(e),
                data=None
            ))

class RetrieveDetailedPostContent(generics.RetrieveAPIView):
    queryset = PostContent.objects.all()
    permission_classes=[IsAuthenticated]
    serializer_class = PostContentSerializer
    lookup_field = "pk"

    @extend_schema(tags=[tag_names['post']], operation_id="Retrieve a single Post")
    def get(self, request, *args, **kwargs):
        post = self.get_object()
        try:
            serializer = self.get_serializer(post)
            data = serializer.data
            return Response(custom_response(
                status_mthd=status.HTTP_200_OK,
                status="success",
                mssg="Post retrieved successfully",
                data=post.post_profile()
            ))
        except Exception as e:
            return Response(custom_response(
                status_mthd=status.HTTP_400_BAD_REQUEST,
                status="error",
                mssg=str(e),
                data=None
            ))
    
class DeletePostContentView(generics.DestroyAPIView):
    queryset = PostContent.objects.all()
    permission_classes=[IsAuthenticated]
    serializer_class = PostContentSerializer
    lookup_field = "pk"

    @extend_schema(tags=[tag_names['post']], operation_id="Delete a Post")
    def delete(self, request, *args, **kwargs):
        instance = self.get_object()
        self.perform_destroy(instance)
        return Response(
            {"message": "Post deleted successfully"},
            status=status.HTTP_204_NO_CONTENT
        )
