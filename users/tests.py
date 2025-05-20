from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase

from .models import CustomUser


class CustomUserViewSetTests(APITestCase):

    def setUp(self):
        # Создаем тестовых пользователей с обязательными полями email и username
        self.admin_user = CustomUser.objects.create_user(
            email="admin@example.com",  # Обязательное поле email
            username="admin",  # Обязательное поле username
            password="adminpass",
            is_staff=True,
        )
        self.normal_user = CustomUser.objects.create_user(
            email="user@example.com",  # Обязательное поле email
            username="user",  # Обязательное поле username
            password="userpass",
        )
        self.create_url = reverse("users:customuser-list")

    def test_create_user(self):
        # Тест на создание пользователя
        data = {
            "username": "newuser",
            "email": "newuser@example.com",  # Обязательное поле email
            "password": "newpassword",
        }
        response = self.client.post(self.create_url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertTrue(CustomUser.objects.filter(username="newuser").exists())

    def test_create_user_unauthenticated(self):
        # Тест на создание пользователя без аутентификации
        self.client.logout()
        data = {
            "username": "newuser",
            "email": "newuser@example.com",  # Обязательное поле email
            "password": "newpassword",
        }
        response = self.client.post(self.create_url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
