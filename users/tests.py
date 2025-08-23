from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase
from users.models import CustomUser

class CustomUserViewSetTests(APITestCase):
    """
    Тесты для вьюсета управления пользователями.
    """

    def setUp(self):
        """
        Настройка тестовых данных перед выполнением тестов.
        Создает тестовых пользователей: администратора и обычного пользователя.
        """
        self.admin_user = CustomUser.objects.create_user(
            email="admin@example.com",
            username="admin",
            password="adminpass",
            is_staff=True,
        )
        self.normal_user = CustomUser.objects.create_user(
            email="user@example.com",
            username="user",
            password="userpass",
        )
        self.create_url = reverse("users:customuser-list")

    def test_create_user(self):
        """
        Тест на создание нового пользователя.
        Ожидается, что пользователь будет успешно создан и вернется статус 201.
        """
        data = {
            "username": "newuser",
            "email": "newuser@example.com",
            "password": "newpassword",
        }
        response = self.client.post(self.create_url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertTrue(CustomUser.objects.filter(username="newuser").exists())

    def test_create_user_unauthenticated(self):
        """
        Тест на создание пользователя без аутентификации.
        Ожидается, что пользователь будет успешно создан и вернется статус 201.
        """
        self.client.logout()
        data = {
            "username": "newuser",
            "email": "newuser@example.com",
            "password": "newpassword",
        }
        response = self.client.post(self.create_url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_create_user_with_existing_email(self):
        """
        Тест на создание пользователя с уже существующим email.
        Ожидается, что вернется статус 400.
        """
        data = {
            "username": "anotheruser",
            "email": "user@example.com",
            "password": "newpassword",
        }
        response = self.client.post(self.create_url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_create_user_without_email(self):
        """
        Тест на создание пользователя без email.
        Ожидается, что вернется статус 400.
        """
        data = {
            "username": "newuser",
            "password": "newpassword",
        }
        response = self.client.post(self.create_url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_create_user_without_password(self):
        """
        Тест на создание пользователя без пароля.
        Ожидается, что вернется статус 400.
        """
        data = {
            "username": "newuser",
            "email": "newuser@example.com",
        }
        response = self.client.post(self.create_url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_create_user_with_short_password(self):
        """
        Тест на создание пользователя с коротким паролем.
        Ожидается, что вернется статус 400.
        """
        data = {
            "username": "shortpassuser",
            "email": "shortpassuser@example.com",
            "password": "short",  # Короткий пароль
        }
        response = self.client.post(self.create_url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
