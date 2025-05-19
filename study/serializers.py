from rest_framework import serializers

from .models import Answer, Material, Question, Review, Test, Theme


class ThemeSerializer(serializers.ModelSerializer):
    """
    Сериализатор для модели темы изучения.

    Поля:
        id (int): Уникальный идентификатор темы.
        title (str): Название темы.
        preview_image (ImageField): Изображение-превью темы.
        description (str): Описание темы.
        updated_at (datetime): Дата и время последнего обновления темы.
    """

    class Meta:
        model = Theme
        fields = ["id", "title", "preview_image", "description", "updated_at"]


class MaterialSerializer(serializers.ModelSerializer):
    """
    Сериализатор для модели материалов.

    Поля:
        title (str): Название материала.
        content (str): Содержимое материала (для статей).
        video_url (str): URL видео (если это видео).
        thema (Theme): Тема, к которой принадлежит материал.
        material_type (str): Тип материала (например, "video", "article", "test").
        description (str): Описание материала (для уроков).
        preview_image (ImageField): Изображение-превью материала (для уроков).
    """

    class Meta:
        model = Material
        fields = [
            "title",
            "content",
            "video_url",
            "thema",
            "material_type",
            "description",
            "preview_image",
        ]


class ReviewSerializer(serializers.ModelSerializer):
    """
    Сериализатор для модели отзывов.

    Поля:
        user (User): Пользователь, оставивший отзыв.
        theme (Theme): Тема, к которой относится отзыв.
        rating (int): Оценка курса.
        content (str): Содержимое отзыва.
        created_at (datetime): Дата и время создания отзыва.
    """

    class Meta:
        model = Review
        fields = ["user", "theme", "rating", "content", "created_at"]


class TestSerializer(serializers.ModelSerializer):
    """
    Сериализатор для модели теста.

    Поля:
        title (str): Название теста.
        material (Material): Материал, к которому принадлежит тест.
        created_at (datetime): Дата и время создания теста.
        updated_at (datetime): Дата и время последнего обновления теста.
    """

    class Meta:
        model = Test
        fields = ["title", "material", "created_at", "updated_at"]

class AnswerSerializer(serializers.ModelSerializer):
    """
    Сериализатор для модели варианта ответа.

    Поля:
        question (Question): Вопрос, к которому принадлежит вариант ответа.
        answer_text (str): Текст варианта ответа.
        is_correct (bool): Является ли вариант ответа правильным.
    """

    class Meta:
        model = Answer
        fields = ["question", "answer_text", "is_correct"]
        read_only_fields = ["question"]

class QuestionSerializer(serializers.ModelSerializer):
    answers = AnswerSerializer(many=True)  # Убираем read_only, чтобы можно было создавать/обновлять ответы

    class Meta:
        model = Question
        fields = ["test", "question_text", "created_at", "updated_at", "answers"]

    def create(self, validated_data):
        answers_data = validated_data.pop('answers')
        question = Question.objects.create(**validated_data)
        for answer_data in answers_data:
            Answer.objects.create(question=question, **answer_data)
        return question

    def update(self, instance, validated_data):
        answers_data = validated_data.pop('answers', None)
        instance.question_text = validated_data.get('question_text', instance.question_text)
        instance.save()

        if answers_data is not None:
            # Удаляем старые ответы
            instance.answers.all().delete()
            # Создаем новые ответы
            for answer_data in answers_data:
                Answer.objects.create(question=instance, **answer_data)

        return instance


class CheckAnswersSerializer(serializers.Serializer):
    """
    Сериализатор для проверки ответов на тест.

    Поля:
        answers (dict): Словарь, где ключ - ID вопроса, а значение - список ID выбранных ответов.
    """
    answers = serializers.DictField(child=serializers.ListField(child=serializers.IntegerField()))

    def validate_answers(self, value):

        question_ids = value.keys()
        if not Question.objects.filter(id__in=question_ids).exists():
            raise serializers.ValidationError("Некоторые вопросы не найдены.")
        return value

