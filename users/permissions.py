from rest_framework import permissions


class IsOwner(permissions.BasePermission):
    """
    Разрешение, позволяющее доступ только владельцу объекта.
    """

    def has_object_permission(self, request, view, obj):
        return obj.owner == request.user


class IsAdmin(permissions.BasePermission):
    """
    Разрешение, позволяющее доступ только администраторам.
    """

    def has_permission(self, request, view):
        return request.user and request.user.is_staff


class IsAuthenticatedUser(permissions.BasePermission):
    """
    Разрешение, позволяющее доступ только аутентифицированным пользователям.
    """

    def has_permission(self, request, view):
        return request.user and request.user.is_authenticated
