from rest_framework import permissions

class IsEventCreatorOrReadOnly(permissions.BasePermission):
    def has_object_permission(self, request, view, obj):
        if request.method in permissions.SAFE_METHODS:
            return True
        return obj.creator == request.user


permission_classes = [
    permissions.IsAuthenticatedOrReadOnly, IsEventCreatorOrReadOnly]
