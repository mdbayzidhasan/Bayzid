from rest_framework import permissions


class IsOwner(permissions.BasePermission):
    """Object-level permission: only the owning user may access/modify."""

    def has_object_permission(self, request, view, obj):
        owner = getattr(obj, "user", None) or getattr(obj, "buyer", None)
        return owner == request.user


class IsSeller(permissions.BasePermission):
    """Allows access only to users with an approved seller profile."""

    def has_permission(self, request, view):
        return bool(
            request.user
            and request.user.is_authenticated
            and hasattr(request.user, "seller_profile")
            and request.user.seller_profile.is_approved
        )


class IsProductOwnerSeller(permissions.BasePermission):
    """Only the seller who owns a product may edit/delete it."""

    def has_object_permission(self, request, view, obj):
        if request.method in permissions.SAFE_METHODS:
            return True
        return obj.seller.user == request.user


class IsAdminOrReadOnly(permissions.BasePermission):
    def has_permission(self, request, view):
        if request.method in permissions.SAFE_METHODS:
            return True
        return bool(request.user and request.user.is_staff)
