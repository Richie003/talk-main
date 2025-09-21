from rest_framework import permissions

class IsEventCreatorOrReadOnly(permissions.BasePermission):
    """
    Custom permission to only allow the creator of an event to edit or delete it.

    - SAFE_METHODS (GET, HEAD, OPTIONS) are always allowed.
    - Write permissions are only granted to the user who created the event (obj.creator).
    """
    def has_object_permission(self, request, view, obj):
        if request.method in permissions.SAFE_METHODS:
            return True
        return obj.creator == request.user

# class 
permission_classes = [
    permissions.IsAuthenticatedOrReadOnly, IsEventCreatorOrReadOnly]
