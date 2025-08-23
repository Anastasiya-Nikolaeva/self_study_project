from django.apps import AppConfig


class UsersConfig(AppConfig):
    """
        Конфигурация приложения пользователей.

        Этот класс настраивает параметры приложения 'users' в Django.

        Атрибуты:
            default_auto_field (str): Поле по умолчанию для автоматического
                                      создания идентификаторов. Установлено на
                                      "django.db.models.BigAutoField".
            name (str): Имя приложения, используемое в Django. Установлено на "users".
    """
    default_auto_field = "django.db.models.BigAutoField"
    name = "users"
