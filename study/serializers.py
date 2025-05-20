from rest_framework import serializers

from .models import Answer, Material, Question, Review, Test, TestResult, Theme


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
        rating (int): Оценка темы.
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
    Сериализатор для модели варианта ответа на вопрос теста.

    Поля:
        id (int): Уникальный идентификатор варианта ответа.
        answer_text (str): Текст варианта ответа.
        is_correct (bool): Является ли вариант ответа правильным.
    """

    class Meta:
        model = Answer
        fields = ["id", "answer_text", "is_correct"]


class CheckAnswerSerializer(serializers.Serializer):
    """
    Сериализатор для проверки ответа пользователя на вопрос.

    Поля:
        question_id (int): Уникальный идентификатор вопроса.
        user_answer (str): Ответ пользователя.
    """

    question_id = serializers.IntegerField()
    user_answer = serializers.CharField()


class QuestionSerializer(serializers.ModelSerializer):
    """
    Сериализатор для модели вопроса теста.

    Поля:
        id (int): Уникальный идентификатор вопроса.
        owner (CustomUser): Владелец вопроса.
        test (Test): Тест, к которому принадлежит вопрос.
        question_text (str): Текст вопроса.
        correct_answer (JSONField): Правильный ответ.
        question_type (str): Тип вопроса (multiple_choice или open_ended).
        created_at (datetime): Дата и время создания вопроса.
        updated_at (datetime): Дата и время последнего обновления вопроса.
        answers (list): Список вариантов ответов на вопрос.
    """

    answers = AnswerSerializer(many=True)

    class Meta:
        model = Question
        fields = [
            "id",
            "owner",
            "test",
            "question_text",
            "correct_answer",
            "question_type",
            "created_at",
            "updated_at",
            "answers",
        ]

    def validate(self, data):
        """Валидация данных вопроса."""
        if data.get("question_type") == "multiple_choice":
            correct_answer_id = data.get("correct_answer")
            if correct_answer_id is None:
                raise serializers.ValidationError(
                    "Для вопросов с множественным выбором необходимо указать правильный ответ."
                )

            answer_ids = []
            for index, answer in enumerate(data.get("answers", [])):
                print("Answer:", answer)
                if isinstance(answer, dict):
                    answer_ids.append(index + 1)
                else:
                    raise serializers.ValidationError(
                        "Каждый ответ должен быть словарем."
                    )

            if correct_answer_id not in answer_ids:
                raise serializers.ValidationError(
                    "Правильный ответ должен быть одним из вариантов."
                )
        elif data.get("question_type") == "open_ended":
            if not data.get("correct_answer"):
                raise serializers.ValidationError(
                    "Для открытых вопросов необходимо указать правильный ответ."
                )
        return data

    def create(self, validated_data):
        """Создание нового вопроса и его вариантов ответов."""
        answers_data = validated_data.pop("answers", [])  # Извлекаем данные ответов
        question = Question.objects.create(**validated_data)  # Создаем вопрос
        for index, answer_data in enumerate(answers_data):
            answer_data["id"] = index + 1  # Генерация ID на основе индекса
            Answer.objects.create(question=question, **answer_data)  # Создаем ответы
        return question

    def update(self, instance, validated_data):
        """Обновление существующего вопроса и его вариантов ответов."""
        answers_data = validated_data.pop("answers", None)  # Извлекаем данные ответов
        instance = super().update(instance, validated_data)  # Обновляем вопрос

        if answers_data is not None:
            existing_answers = {answer.id: answer for answer in instance.answers.all()}

            for index, answer_data in enumerate(answers_data):
                answer_data["id"] = index + 1  # Генерация ID на основе индекса
                answer_id = answer_data.get("id")
                if answer_id in existing_answers:
                    # Обновляем существующий ответ
                    answer = existing_answers[answer_id]
                    answer.answer_text = answer_data.get(
                        "answer_text", answer.answer_text
                    )
                    answer.is_correct = answer_data.get("is_correct", answer.is_correct)
                    answer.save()
                else:
                    # Создаем новый ответ
                    Answer.objects.create(question=instance, **answer_data)

            # Удаляем ответы, которые не были переданы в запросе
            for answer in instance.answers.exclude(
                id__in=[ans.get("id") for ans in answers_data]
            ):
                answer.delete()

        return instance


class TestResultSerializer(serializers.ModelSerializer):
    """
    Сериализатор для модели результатов теста.

    Поля:
        id (int): Уникальный идентификатор результата теста.
        user (CustomUser): Пользователь, который прошел тест.
        test (Test): Тест, который был пройден.
        score (int): Набранные баллы.
        created_at (datetime): Дата и время прохождения теста.
    """

    class Meta:
        model = TestResult
        fields = ["id", "user", "test", "score", "created_at"]
        read_only_fields = ["id", "user", "created_at"]
