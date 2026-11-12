from rest_framework import permissions


class IsOwnerOrAdmin(permissions.BasePermission):
    def has_object_permission(self, request, view, obj):
        if request.user.is_admin_user:
            return True
        if hasattr(obj, 'owner'):
            return obj.owner == request.user
        return False


class CanAccessDocument(permissions.BasePermission):
    def has_object_permission(self, request, view, obj):
        return obj.can_be_accessed_by(request.user)


class IsManagerOrAdmin(permissions.BasePermission):
    def has_permission(self, request, view):
        return request.user.is_authenticated and request.user.is_manager
