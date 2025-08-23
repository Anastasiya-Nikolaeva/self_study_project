from rest_framework import permissions, viewsets, status
from rest_framework.response import Response

from .models import CustomUser
from .permissions import IsAdminOrOwner
from .serializers import CustomUserCreateSerializer, CustomUserSerializer


class CustomUserViewSet(viewsets.ModelViewSet):
    """
    Вьюсет для управления пользователями.

    Этот вьюсет предоставляет CRUD операции для модели CustomUser.
    Он управляет правами доступа и выбирает соответствующие сериализаторы
    в зависимости от действия.

    Атрибуты:
        queryset (QuerySet): Набор данных пользователей, используемый для операций.
    """

    queryset = CustomUser.objects.all()

    def get_permissions(self):
        """
        Определяет права доступа для каждого действия.

        Возвращает:
            list: Список разрешений в зависимости от действия:
                - create: Разрешает доступ всем пользователям.
                - update, partial_update, destroy: Требует аутентификации и
                  проверяет, является ли пользователь администратором или владельцем.
                - другие действия: Требует аутентификации.
        """
        if self.action == "create":
            return [permissions.AllowAny()]  # Разрешить создание пользователям без аутентификации
        elif self.action in ["update", "partial_update", "destroy"]:
            return [permissions.IsAuthenticated(), IsAdminOrOwner()]
        else:
            return [permissions.IsAuthenticated()]

    def get_serializer_class(self):
        """
        Определяет сериализатор, который будет использоваться для текущего действия.

        Возвращает:
            Serializer: Сериализатор для создания или стандартный сериализатор.
        """
        if self.action == "create":
            return CustomUserCreateSerializer  # Использовать сериализатор для создания пользователя
        return CustomUserSerializer  # Использовать стандартный сериализатор

    def create(self, request, *args, **kwargs):
        """
        Создает нового пользователя.

        Проверяет данные запроса, создает пользователя и устанавливает
        флаг is_owner, если пользователь - администратор.

        Аргументы:
            request (Request): Запрос с данными для создания пользователя.

        Возвращает:
            Response: Ответ с данными созданного пользователя и статусом 201.
        """
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        # Создаем пользователя
        user = serializer.save()

        # Устанавливаем is_owner только если пользователь - администратор
        if request.user.is_staff:
            user.is_owner = request.data.get("is_owner", False)
            user.save()

        return Response(serializer.data, status=status.HTTP_201_CREATED)

    def update(self, request, *args, **kwargs):
        """
        Обновляет существующего пользователя.

        Проверяет данные запроса и обновляет информацию о пользователе.
        Устанавливает флаг is_owner, если он передан в запросе.

        Аргументы:
            request (Request): Запрос с данными для обновления пользователя.

        Возвращает:
            Response: Ответ с данными обновленного пользователя.
        """
        partial = kwargs.pop("partial", True)  # Установите partial в True
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data, partial=partial)
        serializer.is_valid(raise_exception=True)

        # Устанавливаем флажок is_owner, если он передан в запросе
        if "is_owner" in request.data:
            instance.is_owner = request.data["is_owner"]

        # Сохраняем обновленного пользователя
        self.perform_update(serializer)

        return Response(serializer.data)
