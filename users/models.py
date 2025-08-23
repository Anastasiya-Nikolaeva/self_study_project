from django.contrib.auth.models import AbstractUser, BaseUserManager
from django.db import models


class CustomUserManager(BaseUserManager):
    """
    Менеджер для пользовательской модели CustomUser.

    Методы:
        create_user: Создает и сохраняет обычного пользователя с указанным email и паролем.
        create_superuser: Создает и сохраняет суперпользователя (администратора) с указанным email и паролем.
    """

    def create_user(self, email, username, password=None, **extra_fields):
        """
        Создает и сохраняет обычного пользователя с указанным email и паролем.

        Аргументы:
            email (str): Адрес электронной почты пользователя.
            username (str): Имя пользователя.
            password (str, optional): Пароль пользователя.
            **extra_fields: Дополнительные поля для пользователя.

        Возвращает:
            CustomUser: Созданный пользователь.
        """
        if not email:
            raise ValueError("Поле электронной почты должно быть задано")
        if not username:
            raise ValueError("Поле имени пользователя должно быть задано")
        if password is None:
            raise ValueError("Пароль должен быть задан")

        email = self.normalize_email(email)
        user = self.model(email=email, username=username, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, username, password=None, **extra_fields):
        """
        Создает и сохраняет суперпользователя (администратора) с указанным email и паролем.

        Аргументы:
            email (str): Адрес электронной почты суперпользователя.
            username (str): Имя пользователя суперпользователя.
            password (str, optional): Пароль суперпользователя.
            **extra_fields: Дополнительные поля для суперпользователя.

        Возвращает:
            CustomUser: Созданный суперпользователь.
        """
        extra_fields.setdefault("is_staff", True)
        extra_fields.setdefault("is_superuser", True)
        return self.create_user(email, username, password, **extra_fields)

    def create_owner(self, email, username, password=None, **extra_fields):
        """
        Создает и сохраняет пользователя-владельца с указанным email и паролем.

        Аргументы:
            email (str): Адрес электронной почты владельца.
            username (str): Имя пользователя владельца.
            password (str, optional): Пароль владельца.
            **extra_fields: Дополнительные поля для владельца.

        Возвращает:
            CustomUser: Созданный владелец.
        """
        if not email:
            raise ValueError("Поле электронной почты должно быть задано")
        if not username:
            raise ValueError("Поле имени пользователя должно быть задано")
        if password is None:
            raise ValueError("Пароль должен быть задан")

        email = self.normalize_email(email)
        owner = self.model(email=email, username=username, **extra_fields)
        owner.set_password(password)
        owner.is_owner = True
        owner.save(using=self._db)
        return owner


class CustomUser(AbstractUser):
    """
    Пользовательская модель пользователя.

    Атрибуты:
        username (str): Имя пользователя (уникальное).
        email (str): Адрес электронной почты пользователя (уникальный).
        phone (str): Номер телефона пользователя (необязательный).
        city (str): Город пользователя (необязательный).
        avatar (ImageField): Фото пользователя (необязательное).
        is_owner (bool): Является ли пользователь преподавателем.

    """

    username = models.CharField(max_length=150, unique=True, default="default_username")
    email = models.EmailField(
        unique=True, verbose_name="Почта", help_text="Укажите почту"
    )
    phone = models.CharField(
        max_length=15,
        blank=True,
        null=True,
        verbose_name="Телефон",
        help_text="Укажите номер телефона",
    )
    city = models.CharField(
        max_length=100,
        blank=True,
        null=True,
        verbose_name="Город",
        help_text="Укажите город",
    )
    avatar = models.ImageField(
        upload_to="avatars/",
        blank=True,
        null=True,
        verbose_name="Фото",
        help_text="Загрузите фотографию",
    )
    is_owner = models.BooleanField(default=False, verbose_name="Владелец материалов")

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = ["username"]

    objects = CustomUserManager()

    def __str__(self):
        return self.email
