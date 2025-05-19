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
        """
        if self.action == "create":
            return [permissions.AllowAny()]
        elif self.action in ["update", "partial_update", "destroy"]:
            return [permissions.IsAuthenticated(), IsOwner() | IsAdmin()]
        else:
            return [permissions.IsAuthenticated()]

    def get_serializer_class(self):
        """
        Использует разные сериализаторы для разных действий.
        """
        if self.action == "create":
            return CustomUserCreateSerializer
        return super().get_serializer_class()

    def get_queryset(self):
        """
        Ограничивает выборку пользователей для аутентифицированных пользователей.
        """
        user = self.request.user
        if user.is_authenticated:
            if user.is_staff:
                return CustomUser.objects.all()
            return CustomUser.objects.filter(id=user.id)
        return CustomUser.objects.none()
