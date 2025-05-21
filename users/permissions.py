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


class IsAdminOrOwner(permissions.BasePermission):
    """
    Разрешение, которое позволяет только администраторам или владельцам
    вносить изменения в объект.
    """

    def has_permission(self, request, view):
        # Разрешить доступ на чтение всем
        if request.method in permissions.SAFE_METHODS:
            return True

        # Проверяем, есть ли pk в URL
        if 'pk' in view.kwargs:
            # Получаем queryset и проверяем, существует ли объект
            queryset = view.get_queryset()
            obj = queryset.filter(pk=view.kwargs['pk']).first()
            if obj is not None:
                return request.user and (request.user.is_staff or request.user == obj.owner)

        return False  # Если pk нет или объект не найден, доступ запрещен


class IsAuthenticatedForRead(permissions.BasePermission):
    """
    Разрешение, позволяющее доступ только аутентифицированным пользователям для чтения.
    """

    def has_permission(self, request, view):
        return request.user and request.user.is_authenticated
