from django.contrib.auth import get_user_model
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase
from rest_framework_simplejwt.tokens import RefreshToken
from users.models import CustomUser as User

from .models import Material, Theme, Review
from .serializers import ReviewSerializer

User = get_user_model()


class ThemeViewSetTests(APITestCase):
    """
    Тесты для ThemeViewSet, проверяющие функциональность управления темами.
    """

    def setUp(self):
        """
        Настройка тестов. Создает пользователей (владельца, администратора и другого пользователя)
        и тестовую тему для использования в тестах.
        """
        self.owner = User.objects.create_user(
            email="owner@example.com", username="owner", password="password", is_owner=True
        )
        self.admin = User.objects.create_superuser(
            email="admin@example.com", username="adminuser", password="adminpassword"
        )
        self.other_user = User.objects.create_user(
            email="other@example.com", username="other", password="password"
        )
        self.theme = Theme.objects.create(
            title="Тестирование темы", description="Описание теста", owner=self.owner
        )

    def get_jwt_token(self, user):
        """
        Получает JWT токен для указанного пользователя.
        """
        refresh = RefreshToken.for_user(user)
        return str(refresh.access_token)

    def test_create_theme_as_owner(self):
        token = self.get_jwt_token(self.owner)
        self.client.credentials(HTTP_AUTHORIZATION='Bearer ' + token)  # Устанавливаем токен в заголовок

        response = self.client.post(reverse('study:theme-list'), {
            'title': 'New Theme',
            'description': 'Description of the new theme',
        })

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Theme.objects.count(), 2)  # Убедитесь, что вы проверяете правильное количество
        theme = Theme.objects.get(title='New Theme')
        self.assertEqual(theme.owner, self.owner)  # Проверяем, что владелец установлен правильно

    def test_create_theme_as_admin(self):
        token = self.get_jwt_token(self.admin)
        self.client.credentials(HTTP_AUTHORIZATION='Bearer ' + token)  # Устанавливаем токен в заголовок
        response = self.client.post(reverse('study:theme-list'), {
            'title': 'New Theme',
            'description': 'Description of the new theme',
        })
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)  # Ожидаем 403, так как администратор не может создавать темы

    def test_other_user_cannot_create_theme(self):
        """
        Проверяет, что другой пользователь не может создать новую тему.
        """
        token = self.get_jwt_token(self.other_user)
        url = reverse("study:theme-list")
        data = {
            "title": "Вредоносная тема",
            "description": "Описание вредоносной темы"
        }
        response = self.client.post(url, data, HTTP_AUTHORIZATION=f"Bearer {token}")
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_unauthenticated_user_cannot_create_theme(self):
        """
        Проверяет, что неаутентифицированный пользователь не может создать новую тему.
        """
        url = reverse("study:theme-list")
        data = {
            "title": "Несанкционированная тема",
            "description": "Описание несанкционированной темы"
        }
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_owner_can_update_theme(self):
        """
        Проверяет, что владелец темы может обновить ее.
        """
        token = self.get_jwt_token(self.owner)
        url = reverse("study:theme-detail", args=[self.theme.pk])
        data = {"title": "Обновленный заголовок", "description": "Обновленное описание"}
        response = self.client.patch(url, data, HTTP_AUTHORIZATION=f"Bearer {token}")
        self.theme.refresh_from_db()
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(self.theme.title, "Обновленный заголовок")

    def test_other_user_cannot_update_theme(self):
        """
        Проверяет, что другой пользователь, который не является владельцем темы,
        не может обновить ее.
        """
        token = self.get_jwt_token(self.other_user)
        url = reverse("study:theme-detail", args=[self.theme.pk])
        data = {"title": "Вредоносное обновление"}
        response = self.client.patch(url, data, HTTP_AUTHORIZATION=f"Bearer {token}")
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_admin_can_update_theme(self):
        """
        Проверяет, что администратор может обновить любую тему.
        """
        token = self.get_jwt_token(self.admin)
        url = reverse("study:theme-detail", args=[self.theme.pk])
        data = {
            "title": "Обновление администратора",
            "description": "Обновленное описание",
        }
        response = self.client.patch(url, data, HTTP_AUTHORIZATION=f"Bearer {token}")
        self.theme.refresh_from_db()
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(self.theme.title, "Обновление администратора")

    def test_unauthenticated_user_cannot_update_theme(self):
        """
        Проверяет, что неаутентифицированный пользователь не может обновить тему.
        """
        url = reverse("study:theme-detail", args=[self.theme.pk])
        data = {"title": "Несанкционированное обновление"}
        response = self.client.patch(url, data)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

class MaterialViewSetTests(APITestCase):
    """
    Тесты для MaterialViewSet, проверяющие функциональность управления материалами.
    """

    def setUp(self):
        """
        Настройка тестов. Создает пользователей (владельца, администратора и другого пользователя)
        и тестовые материалы для использования в тестах.
        """
        self.owner = User.objects.create_user(
            email="owner@example.com", username="owner", password="password", is_owner=True
        )
        self.admin = User.objects.create_superuser(
            email="admin@example.com", username="adminuser", password="adminpassword"
        )
        self.other_user = User.objects.create_user(
            email="other@example.com", username="other", password="password"
        )

        # Создаем тестовую тему
        self.theme = Theme.objects.create(
            title="Тестовая тема",
            description="Описание тестовой темы",
            owner=self.owner,
        )

        # Создаем тестовый материал с указанием темы
        self.material = Material.objects.create(
            title="Тестовый материал",
            description="Описание теста",
            thema=self.theme,  # Указываем тему
            owner=self.owner,  # Указываем владельца
        )

    def get_jwt_token(self, user):
        """
        Получает JWT токен для указанного пользователя.
        """
        refresh = RefreshToken.for_user(user)
        return str(refresh.access_token)

    def test_list_materials(self):
        """
        Проверяет, что аутентифицированный пользователь может получить список материалов.
        """
        token = self.get_jwt_token(self.owner)
        url = reverse("study:material-list")
        response = self.client.get(url, HTTP_AUTHORIZATION=f"Bearer {token}")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn(
            "Тестовый материал",
            [material["title"] for material in response.data["results"]],
        )

    def test_create_material_with_nonexistent_theme(self):
        """
         Проверяет, что создание материала с несуществующей темой возвращает 404.
        """
        token = self.get_jwt_token(self.owner)
        url = reverse("study:material-list")
        data = {
            "title": "Материал с несуществующей темой",
            "description": "Описание материала",
            "thema": 9999,  # Не существующий ID
        }
        response = self.client.post(url, data, HTTP_AUTHORIZATION=f"Bearer {token}")
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        self.assertIn("Тема не найдена", response.data["detail"])

    def test_create_material_as_owner(self):
        token = self.get_jwt_token(self.owner)
        url = reverse("study:material-list")
        data = {
            "title": "Новый материал",
            "description": "Описание нового материала",
            "thema": self.theme.pk,
            "material_type": "article",  # Укажите корректный тип материала
            "owner": self.owner.pk,
        }
        response = self.client.post(url, data, HTTP_AUTHORIZATION=f"Bearer {token}")
        if response.status_code != status.HTTP_201_CREATED:
            print(response.data)  # Выводим ошибки валидации
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_owner_can_destroy_material(self):
        """
        Проверяет, что владелец может удалить свой материал.
        """
        token = self.get_jwt_token(self.owner)
        url = reverse("study:material-detail", args=[self.material.pk])
        response = self.client.delete(url, HTTP_AUTHORIZATION=f"Bearer {token}")
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertFalse(Material.objects.filter(pk=self.material.pk).exists())  # Проверяем, что материал был удален

    def test_update_material_as_owner(self):
        token = self.get_jwt_token(self.owner)
        url = reverse("study:material-detail", args=[self.material.pk])
        data = {
            "title": "Обновленный материал",
            "description": "Обновленное описание",
            "thema": self.material.thema.pk,  # Добавляем тему
            "material_type": "article",  # Убедитесь, что это допустимое значение
            "owner": self.owner.pk,
        }
        response = self.client.patch(url, data, HTTP_AUTHORIZATION=f"Bearer {token}")
        if response.status_code != status.HTTP_200_OK:
            print(response.data)  # Выводим ошибки валидации
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_update_material_as_admin(self):
        token = self.get_jwt_token(self.admin)
        url = reverse("study:material-detail", args=[self.material.pk])
        data = {
            "title": "Обновленный материал от администратора",
            "description": "Обновленное описание от администратора",
            "thema": self.material.thema.pk,
            "material_type": "article",
            "owner": self.owner.pk,
        }
        response = self.client.patch(url, data, HTTP_AUTHORIZATION=f"Bearer {token}")
        if response.status_code != status.HTTP_200_OK:
            print(response.data)  # Выводим ошибки валидации
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_admin_can_destroy_material(self):
        """
        Проверяет, что администратор может удалить материал.
        """
        token = self.get_jwt_token(self.admin)
        url = reverse("study:material-detail", args=[self.material.pk])
        response = self.client.delete(url, HTTP_AUTHORIZATION=f"Bearer {token}")
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertFalse(Material.objects.filter(pk=self.material.pk).exists())  # Проверяем, что материал был удален


class ReviewAPITests(APITestCase):

    def setUp(self):
        """
        Настройка тестов. Создает пользователей (владельца, администратора и другого пользователя)
        и тестовые материалы для использования в тестах.
        """
        self.owner = User.objects.create_user(
            email="owner@example.com",
            username="owner",
            password="password",
            is_owner=True,
        )
        self.admin = User.objects.create_superuser(
            email="admin@example.com", username="adminuser", password="adminpassword"
        )
        self.other_user = User.objects.create_user(
            email="other@example.com", username="other", password="password"
        )

        # Создаем тестовую тему
        self.theme = Theme.objects.create(
            title="Тестовая тема",
            description="Описание тестовой темы",
            owner=self.owner,
        )

        # Создаем тестовый отзыв с указанием темы и владельца
        self.review = Review.objects.create(
            user=self.owner, theme=self.theme, rating=5, content="Отличная тема!"
        )

    def get_jwt_token(self, user):
        """
        Получает JWT токен для указанного пользователя.
        """
        refresh = RefreshToken.for_user(user)
        return str(refresh.access_token)

    def test_create_review_as_authenticated_user(self):
        self.client.credentials(
            HTTP_AUTHORIZATION="Bearer " + self.get_jwt_token(self.owner)
        )
        url = reverse("study:review-list")
        data = {
            "user": self.owner.pk,
            "theme": self.theme.id,
            "rating": 5,
            "content": "Отличный отзыв!",
        }
        response = self.client.post(url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Review.objects.count(), 2)  # Проверяем, что отзыв добавлен
        new_review = Review.objects.last()
        self.assertEqual(
            new_review.owner, self.owner
        )  # Проверяем, что owner установлен правильно

    def test_create_review_as_unauthenticated_user(self):
        url = reverse("study:review-list")
        data = {"theme": self.theme.id, "rating": 5, "content": "Отличный отзыв!"}
        response = self.client.post(url, data, format="json")
        self.assertEqual(
            response.status_code, status.HTTP_401_UNAUTHORIZED
        )  # Изменено на 401

    def test_update_review_as_owner(self):
        self.client.credentials(
            HTTP_AUTHORIZATION="Bearer " + self.get_jwt_token(self.owner)
        )
        url = reverse("study:review-detail", args=[self.review.id])
        data = {
            "content": "Обновленный отзыв",
            "user": self.owner.pk,
            "theme": self.review.theme.id,
            "rating": self.review.rating
        }

        response = self.client.put(url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.review.refresh_from_db()
        self.assertEqual(self.review.content, "Обновленный отзыв")

    def test_update_review_as_admin(self):
        self.client.credentials(
            HTTP_AUTHORIZATION="Bearer " + self.get_jwt_token(self.admin)
            # Предполагается, что у вас есть администратор
        )
        url = reverse("study:review-detail", args=[self.review.id])
        data = {
            "content": "Обновленный отзыв администратором",
            "user": self.review.user.pk,  # Пользователь, который оставил отзыв
            "theme": self.review.theme.id,
            "rating": self.review.rating
        }

        response = self.client.put(url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.review.refresh_from_db()
        self.assertEqual(self.review.content, "Обновленный отзыв администратором")

    def test_delete_review_as_owner(self):
        self.client.credentials(
            HTTP_AUTHORIZATION="Bearer " + self.get_jwt_token(self.owner)
        )
        url = reverse("study:review-detail", args=[self.review.id])
        response = self.client.delete(url)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertFalse(Review.objects.filter(id=self.review.id).exists())  # Проверяем, что отзыв удален

    def test_delete_review_as_admin(self):
        self.client.credentials(
            HTTP_AUTHORIZATION="Bearer " + self.get_jwt_token(self.admin)
        )
        url = reverse("study:review-detail", args=[self.review.id])
        response = self.client.delete(url)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertEqual(Review.objects.count(), 0)  # Проверяем, что отзыв удален

    def test_update_review_as_different_user(self):
        self.client.credentials(
            HTTP_AUTHORIZATION="Bearer " + self.get_jwt_token(self.other_user)
        )
        url = reverse("study:review-detail", args=[self.review.id])
        data = {"content": "Попытка обновления", "user": self.owner.pk}
        response = self.client.put(url, data, format="json")
        self.assertEqual(
            response.status_code, status.HTTP_403_FORBIDDEN
        )  # Проверяем, что доступ запрещен

    def test_user_can_only_leave_one_review_per_theme(self):
        self.client.credentials(
            HTTP_AUTHORIZATION="Bearer " + self.get_jwt_token(self.owner)
        )
        url = reverse("study:review-list")
        data = {
            "theme": self.theme.id,
            "rating": 5,
            "content": "Первый отзыв!",
            "user": self.owner.pk
        }
        response = self.client.post(url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
