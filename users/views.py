from rest_framework import permissions, viewsets

from .models import CustomUser
from .permissions import IsAdmin, IsOwner
from .serializers import CustomUserCreateSerializer, CustomUserSerializer


class CustomUserViewSet(viewsets.ModelViewSet):
    """
    Вьюсет для управления пользователями.
    """

    queryset = CustomUser.objects.all()
    serializer_class = CustomUserSerializer

    def get_permissions(self):
        """
        Определяет разрешения для действий.

        Возвращает:
            list: Список разрешений для текущего действия.
        """
        if self.action == "create":
            return [permissions.AllowAny()]  # Разрешить создание пользователям без аутентификации
        elif self.action in ["update", "partial_update", "destroy"]:
            return [permissions.IsAuthenticated(), IsOwner(), IsAdmin()]  # Требуется аутентификация и права владельца или администратора
        else:
            return [permissions.IsAuthenticated()]  # Для остальных действий требуется аутентификация

    def get_serializer_class(self):
        """
        Использует разные сериализаторы для разных действий.

        Возвращает:
            Type[serializers.ModelSerializer]: Сериализатор для текущего действия.
        """
        if self.action == "create":
            return CustomUserCreateSerializer  # Использовать сериализатор для создания пользователя
        return super().get_serializer_class()  # Использовать стандартный сериализатор

    def get_queryset(self):
        """
        Ограничивает выборку пользователей для аутентифицированных пользователей.

        Возвращает:
            QuerySet: Выборка пользователей в зависимости от аутентификации.
        """
        user = self.request.user
        if user.is_authenticated:
            if user.is_staff:
                return CustomUser.objects.all()  # Администраторы могут видеть всех пользователей
            return CustomUser.objects.filter(id=user.id)  # Обычные пользователи видят только себя
        return CustomUser.objects.none()  # Неаутентифицированные пользователи не видят никого