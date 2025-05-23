from django.core.exceptions import ValidationError
from rest_framework import serializers

from users.models import CustomUser


class CustomUserSerializer(serializers.ModelSerializer):
    """
    Сериализатор для пользовательской модели CustomUser.

    Поля:
        id (int): Уникальный идентификатор пользователя.
        username (str): Имя пользователя.
        email (str): Адрес электронной почты пользователя.
        phone (str): Номер телефона пользователя (необязательный).
        city (str): Город пользователя (необязательный).
        avatar (ImageField): Фото пользователя (необязательное).
    """

    class Meta:
        model = CustomUser
        fields = [
            "id",
            "username",
            "email",
            "phone",
            "city",
            "avatar",
            "is_owner",
            "is_superuser",
        ]


class CustomUserCreateSerializer(serializers.ModelSerializer):
    """
    Сериализатор для создания нового пользователя.

    Поля:
        username (str): Имя пользователя.
        email (str): Адрес электронной почты пользователя.
        password (str): Пароль пользователя.
        phone (str): Номер телефона пользователя (необязательный).
        city (str): Город пользователя (необязательный).
        avatar (ImageField): Фото пользователя (необязательное).
    """

    class Meta:
        model = CustomUser
        fields = [
            "username",
            "email",
            "password",
        ]

    password = serializers.CharField(write_only=True)

    def validate_email(self, value):
        if CustomUser.objects.filter(email=value).exists():
            raise ValidationError("Пользователь с таким email уже существует.")
        return value

    def validate_password(self, value):
        if len(value) < 8:
            raise ValidationError("Пароль должен содержать не менее 8 символов.")
        return value

    def create(self, validated_data):
        """
        Создание нового пользователя.

        Аргументы:
            validated_data (dict): Данные, прошедшие валидацию.

        Возвращает:
            CustomUser: Созданный пользователь.
        """
        # Удаляем is_owner из validated_data, если оно есть
        is_owner = validated_data.pop("is_owner", False)

        user = CustomUser.objects.create_user(
            email=validated_data["email"],
            username=validated_data["username"],
            password=validated_data["password"],
            phone=validated_data.get("phone"),
            city=validated_data.get("city"),
            avatar=validated_data.get("avatar"),
        )

        # Устанавливаем is_owner только если пользователь - администратор
        if self.context["request"].user.is_staff:
            user.is_owner = is_owner

        user.save()
        return user
