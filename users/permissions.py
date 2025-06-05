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
    Разрешение, которое позволяет администраторам выполнять любые действия,
    а владельцам - только с их собственными объектами.
    """

    def has_permission(self, request, view):
        # Разрешить доступ на чтение всем
        if request.method in permissions.SAFE_METHODS:
            return True

        # Проверяем, аутентифицирован ли пользователь
        if not request.user.is_authenticated:
            return False

        # Разрешаем создание объектов только владельцам
        if request.method == "POST":
            return request.user.is_owner  # Только владельцы могут создавать объекты

        # Для всех остальных методов (PUT, PATCH, DELETE)
        if request.method in ["PUT", "PATCH", "DELETE"]:
            if "pk" in view.kwargs:
                try:
                    obj = view.get_queryset().get(pk=view.kwargs["pk"])
                    return request.user.is_staff or request.user == obj.owner
                except view.get_queryset().model.DoesNotExist:
                    return False  # Объект не найден, доступ запрещен

        return False


class IsAuthenticatedForRead(permissions.BasePermission):
    """
    Разрешение, позволяющее доступ только аутентифицированным пользователям для чтения.
    """

    def has_permission(self, request, view):
        return request.user and request.user.is_authenticated
