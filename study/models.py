from django.conf import settings
from django.db import models
from django.db.models import JSONField


class Theme(models.Model):
    """
    Модель темы изучения.

    Атрибуты:
        title (str): Название темы.
        preview_image (ImageField): Изображение-превью темы.
        description (str): Описание темы.
        updated_at (DateTimeField): Дата и время последнего обновления темы.
        owner (ForeignKey): Владелец темы (преподаватель).
    """

    title = models.CharField(max_length=200)
    preview_image = models.ImageField(
        upload_to="theme_previews/", null=True, blank=True
    )
    description = models.TextField()
    updated_at = models.DateTimeField(auto_now=True)
    owner = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE)

    class Meta:
        ordering = ["title"]  # Порядок по умолчанию по названию материала

    def __str__(self) -> str:
        """Возвращает строковое представление темы (название)."""
        return self.title


class Material(models.Model):
    """
    Модель материалов для обучения.

    Атрибуты:
        title (str): Название материала.
        content (TextField): Содержимое материала (для статей).
        video_url (URLField): URL видео (если это видео).
        thema (Theme): Тема, к которой принадлежит материал.
        material_type (str): Тип материала (например, "video", "article", "test").
        description (TextField): Описание материала (для уроков).
        preview_image (ImageField): Изображение-превью материала (для уроков).
        owner (User): Владелец материала.
    """

    MATERIAL_TYPE_CHOICES = [
        ("video", "Видео"),
        ("article", "Статья"),
        ("test", "Тест"),
    ]

    title = models.CharField(max_length=200)
    content = models.TextField(blank=True, null=True)
    video_url = models.URLField(blank=True, null=True)
    thema = models.ForeignKey(Theme, related_name="materials", on_delete=models.CASCADE)
    material_type = models.CharField(max_length=10, choices=MATERIAL_TYPE_CHOICES)
    description = models.TextField(blank=True, null=True)
    preview_image = models.ImageField(
        upload_to="material_previews/", null=True, blank=True
    )
    owner = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)

    class Meta:
        ordering = ["title"]  # Порядок по умолчанию по названию материала

    def __str__(self) -> str:
        """Возвращает строковое представление материала (название)."""
        return self.title


class Review(models.Model):
    """
    Модель отзывов о темах.

    Атрибуты:
        user (User): Пользователь, оставивший отзыв.
        theme (Theme): Тема, к которой относится отзыв.
        rating (IntegerField): Оценка темы (например, от 1 до 5).
        content (TextField): Содержимое отзыва.
        created_at (DateTimeField): Дата и время создания отзыва.
    """

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        verbose_name="Пользователь",
        related_name="reviews",
    )
    theme = models.ForeignKey(
        Theme, related_name="reviews", on_delete=models.CASCADE, verbose_name="Тема"
    )
    rating = models.IntegerField(
        verbose_name="Оценка",
        choices=[(i, str(i)) for i in range(1, 6)],
    )
    content = models.TextField(blank=True, null=True, verbose_name="Содержимое отзыва")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Дата создания")
    owner = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE
    )

    def save(self, *args, **kwargs):
        if not self.owner and self.user:
            self.owner = self.user
        super().save(*args, **kwargs)

    class Meta:
        ordering = ["created_at"]  # Порядок по умолчанию по созданию отзыва

    def __str__(self) -> str:
        """Возвращает строковое представление отзыва."""
        return f"Отзыв от {self.user} на тему {self.theme}"


class Test(models.Model):
    """
    Модель теста.

    Атрибуты:
        title (str): Название теста.
        material (Material): Материал, к которому принадлежит тест.
        created_at (DateTimeField): Дата и время создания теста.
        updated_at (DateTimeField): Дата и время последнего обновления теста.
        owner (User): Владелец теста.
    """

    title = models.CharField(max_length=200)
    material = models.ForeignKey(
        Material, related_name="tests", on_delete=models.CASCADE
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    owner = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)

    class Meta:
        ordering = ["title"]  # Порядок по умолчанию по названию теста

    def __str__(self) -> str:
        """Возвращает строковое представление теста (название)."""
        return self.title


class Question(models.Model):
    """
    Модель вопроса теста.

    Атрибуты:
        owner (CustomUser): Владелец, которому принадлежит вопрос.
        test (Test): Тест, к которому принадлежит вопрос.
        question_text (str): Текст вопроса.
        correct_answer (JSONField): Правильный ответ (может быть текстом или числом).
        question_type (str): Тип вопроса (multiple_choice или open_ended).
        created_at (DateTimeField): Дата и время создания вопроса.
        updated_at (DateTimeField): Дата и время последнего обновления вопроса.
    """

    QUESTION_TYPE_CHOICES = [
        ("multiple_choice", "Варианты ответа"),
        ("open_ended", "Открытый вопрос"),
    ]

    owner = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, default=1
    )
    test = models.ForeignKey(Test, related_name="questions", on_delete=models.CASCADE)
    question_text = models.TextField()
    correct_answer = JSONField(
        blank=True,
        null=True,
        help_text="Правильный ответ (может быть текстом или числом).",
    )
    question_type = models.CharField(
        max_length=20, choices=QUESTION_TYPE_CHOICES, default="multiple_choice"
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self) -> str:
        """Возвращает строковое представление вопроса (текст вопроса)."""
        return self.question_text


class Answer(models.Model):
    """
    Модель варианта ответа на вопрос теста.

    Атрибуты:
        question (Question): Вопрос, к которому принадлежит вариант ответа.
        answer_text (str): Текст варианта ответа.
        is_correct (bool): Является ли вариант ответа правильным.
    """

    question = models.ForeignKey(
        Question, related_name="answers", on_delete=models.CASCADE
    )
    answer_text = models.CharField(max_length=200)
    is_correct = models.BooleanField(default=False)

    def __str__(self) -> str:
        """Возвращает строковое представление варианта ответа (текст варианта)."""
        return self.answer_text


class TestResult(models.Model):
    """
    Модель для хранения результатов теста пользователя.

    Атрибуты:
        user (CustomUser): Пользователь, который прошел тест.
        test (Test): Тест, который был пройден.
        score (int): Набранные баллы.
        created_at (DateTimeField): Дата и время прохождения теста.
    """

    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    test = models.ForeignKey(Test, on_delete=models.CASCADE)
    score = models.IntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self) -> str:
        """Возвращает строковое представление результата теста."""
        return f"{self.user.username} - {self.test.title} - {self.score} баллов"
