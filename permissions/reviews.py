from rest_framework import permissions

class CanViewProducts(permissions.BasePermission):
    """
    Allows users to view Products only if they belong to the same institution.
    Write access is denied entirely.
    """

    message = "You can only view products from users in your institution."

    def has_object_permission(self, request, view, obj):
        print("Checking view permissions for user:", request.user)
        # Allow read-only access if same university
        if request.method in permissions.SAFE_METHODS:
            user_uni = getattr(request.user, "university", None)
            obj_uni = getattr(obj.user, "university", None)
            return user_uni is not None and obj_uni == user_uni

        # Deny write/delete/etc.
        return False

class CanReviewProducts(permissions.BasePermission):
    """
    Only allow users to review products from their own institution (university).
    """

    message = "You can only review products from your institution."

    def has_permission(self, request, view):
        # Ensure the user has a university assigned
        return hasattr(request.user, "university") and request.user.university is not None

    def has_object_permission(self, request, view, obj):
        # obj is a MarketPlaceProduct
        user_uni = getattr(request.user, "university", None)
        product_owner_uni = getattr(obj.user, "university", None)
        print("User Uni:", user_uni, "Product Owner Uni:", product_owner_uni)
        return user_uni is not None and product_owner_uni == user_uni
    

# permissions_classes = [
#     permissions.IsAuthenticated,
#     permissions.IsAuthenticatedOrReadOnly, CanViewProducts, CanReviewProducts
# ]