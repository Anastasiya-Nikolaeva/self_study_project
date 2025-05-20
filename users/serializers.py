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

    password = serializers.CharField(write_only=True)

    class Meta:
        model = CustomUser
        fields = [
            "username",
            "email",
            "password",
            "phone",
            "city",
            "avatar",
        ]

    def validate_password(self, value):
        """
        Проверка пароля на минимальную длину.

        Аргументы:
            value (str): Пароль пользователя.

        Исключения:
            ValidationError: Если пароль содержит менее 8 символов.
        """
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
        user = CustomUser.objects.create_user(
            email=validated_data["email"],
            username=validated_data["username"],
            password=validated_data["password"],
            phone=validated_data.get("phone"),
            city=validated_data.get("city"),
            avatar=validated_data.get("avatar"),
        )
        return user
