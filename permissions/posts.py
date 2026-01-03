from rest_framework import permissions

class CanViewPostContent(permissions.BasePermission):
    """
    Allows users to view PostContent only if they belong to the same institution.
    Write access is denied entirely.
    """

    message = "You can only view posts from users in your institution."

    def has_object_permission(self, request, view, obj):
        # Allow read-only access if same university
        if request.method in permissions.SAFE_METHODS:
            user_uni = getattr(request.user, "university", None)
            obj_uni = getattr(obj.user, "university", None)
            return user_uni is not None and obj_uni == user_uni

        # Deny write/delete/etc.
        return False

class CanEditDeletePostComment(permissions.BasePermission):
    """
    Custom permission to only allow the creator of an event to edit or delete it.

    - SAFE_METHODS (GET, HEAD, OPTIONS) are always allowed.
    - Write permissions are only granted to the user who created the event (obj.user).
    """
    def has_object_permission(self, request, view, obj):
        if request.method in permissions.SAFE_METHODS:
            return True
        return obj.user == request.user