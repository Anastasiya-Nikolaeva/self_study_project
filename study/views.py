import logging

from rest_framework import filters, permissions, status, viewsets
from rest_framework.response import Response

from users.permissions import IsAdmin, IsAdminOrOwner, IsAuthenticatedForRead, IsOwner

from .models import Answer, Material, Question, Review, Test, TestResult, Theme
from .pagination import StandardResultsSetPagination
from .serializers import (
    CheckAnswerSerializer,
    MaterialSerializer,
    QuestionSerializer,
    ReviewSerializer,
    TestResultSerializer,
    TestSerializer,
    ThemeSerializer,
)

logger = logging.getLogger(__name__)


class ThemeViewSet(viewsets.ModelViewSet):
    """
    ViewSet для управления темами изучения.
    """

    queryset = Theme.objects.all()
    serializer_class = ThemeSerializer
    permission_classes = [IsAdminOrOwner]
    filter_backends = [filters.SearchFilter]
    search_fields = ["title", "description"]
    pagination_class = StandardResultsSetPagination

    def create(self, request, *args, **kwargs):
        # Устанавливаем владельца темы на текущего пользователя
        request.data['owner'] = request.user.id
        return super().create(request, *args, **kwargs)

    def perform_update(self, serializer):
        # Обновляем только те поля, которые можно обновить
        serializer.save()


class MaterialViewSet(viewsets.ModelViewSet):
    """
    ViewSet для управления материалами.

    Доступные действия:
        - list: Получить список всех материалов.
        - create: Создать новый материал.
        - retrieve: Получить информацию о конкретном материале.
        - update: Обновить информацию о материале.
        - destroy: Удалить материал.
    """

    queryset = Material.objects.all()
    serializer_class = MaterialSerializer
    permission_classes = [IsAdminOrOwner]
    pagination_class = StandardResultsSetPagination


class ReviewViewSet(viewsets.ModelViewSet):
    """
    ViewSet для управления отзывами.

    Доступные действия:
        - list: Получить список всех отзывов.
        - create: Создать новый отзыв.
        - retrieve: Получить информацию о конкретном отзыве.
        - update: Обновить информацию о отзыве.
        - destroy: Удалить отзыв.
    """

    queryset = Review.objects.all()
    serializer_class = ReviewSerializer
    pagination_class = StandardResultsSetPagination

    def get_permissions(self):
        if self.request.method in ["POST", "PUT", "PATCH", "DELETE"]:
            # Разрешить доступ только владельцам или администраторам
            self.permission_classes = [IsOwner | IsAdmin]
        else:
            # Все могут просматривать отзывы
            self.permission_classes = [permissions.AllowAny]
        return super().get_permissions()


class TestViewSet(viewsets.ModelViewSet):
    """
    ViewSet для управления тестами.

    Доступные действия:
        - list: Получить список всех тестов.
        - create: Создать новый тест.
        - retrieve: Получить информацию о конкретном тесте.
        - update: Обновить информацию о тесте.
        - destroy: Удалить тест.
    """

    queryset = Test.objects.all()
    serializer_class = TestSerializer
    permission_classes = [IsAdminOrOwner]
    pagination_class = StandardResultsSetPagination

    def create(self, request, *args, **kwargs):
        """
        Создание нового теста.

        Аргументы:
            request: HTTP-запрос с данными теста.

        Возвращает:
            Response: Ответ с данными созданного теста и статусом 201.
        """
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)


class AnswerViewSet(viewsets.ViewSet):
    """
    ViewSet для управления ответами на вопросы тестов.

    Доступные действия:
        - check_answer: Проверить ответ пользователя на вопрос.
    """

    permission_classes = [IsAdminOrOwner]

    def check_answer(self, request):
        """
        Проверка ответа пользователя на вопрос.

        Аргументы:
            request: HTTP-запрос с данными для проверки ответа.

        Возвращает:
            Response: Ответ с результатом проверки и текущим счетом.
        """
        serializer = CheckAnswerSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        question_id = serializer.validated_data["question_id"]
        user_answer = (
            serializer.validated_data["user_answer"].strip().lower()
        )  # Приводим к нижнему регистру

        try:
            question = Question.objects.get(id=question_id)
        except Question.DoesNotExist:
            return Response(
                {"error": "Вопрос не найден."}, status=status.HTTP_404_NOT_FOUND
            )

        # Проверяем, является ли ответ пользователя правильным
        is_correct = False
        if question.question_type == "open_ended":
            # Для открытых вопросов
            correct_answer = question.correct_answer  # Получаем правильный ответ
            if correct_answer is not None:  # Проверяем, что правильный ответ не None
                correct_answer = (
                    correct_answer.strip().lower()
                )  # Приводим к нижнему регистру
                if user_answer == correct_answer:
                    is_correct = True
        else:
            # Для закрытых вопросов
            correct_answer_id = question.correct_answer
            if (
                correct_answer_id is not None
                and user_answer == str(correct_answer_id).strip().lower()
            ):  # Сравниваем с правильным ответом
                is_correct = True

        # Обновляем или создаем запись о результате теста
        test_id = question.test.id  # Получаем ID теста
        user = request.user  # Получаем текущего пользователя

        test_result, created = TestResult.objects.get_or_create(
            user=user, test=question.test
        )

        if is_correct:
            test_result.score += 1  # Увеличиваем баллы за правильный ответ
            test_result.save()

            return Response(
                {"result": "Правильный ответ!", "score": test_result.score},
                status=status.HTTP_200_OK,
            )
        else:
            return Response(
                {"result": "Неправильный ответ.", "score": test_result.score},
                status=status.HTTP_200_OK,
            )


class QuestionViewSet(viewsets.ModelViewSet):
    """
    ViewSet для управления вопросами тестов.

    Доступные действия:
        - list: Получить список всех вопросов.
        - create: Создать новый вопрос.
        - retrieve: Получить информацию о конкретном вопросе.
        - update: Обновить информацию о вопросе.
        - destroy: Удалить вопрос.
    """

    queryset = Question.objects.all()
    serializer_class = QuestionSerializer
    permission_classes = [IsAdminOrOwner]

    def create(self, request, *args, **kwargs):
        """
        Создание нового вопроса.

        Аргументы:
            request: HTTP-запрос с данными вопроса.

        Возвращает:
            Response: Ответ с данными созданного вопроса и статусом 201.
        """
        # Извлекаем данные из запроса
        data = request.data

        # Проверяем, что правильный ответ указан
        if data.get("question_type") == "multiple_choice":
            correct_answer_id = data.get("correct_answer")
            answers = data.get("answers", [])
            if correct_answer_id is not None and not any(
                answer["id"] == correct_answer_id for answer in answers
            ):
                return Response(
                    {"error": "Правильный ответ должен быть одним из вариантов."},
                    status=status.HTTP_400_BAD_REQUEST,
                )
        elif data.get("question_type") == "open_ended":
            correct_answer = data.get("correct_answer")
            if correct_answer is None:
                return Response(
                    {
                        "error": "Для открытого вопроса необходимо указать правильный ответ."
                    },
                    status=status.HTTP_400_BAD_REQUEST,
                )

        # Сериализация и создание вопроса
        serializer = self.get_serializer(data=data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    def list(self, request, *args, **kwargs):
        """
        Получение списка всех вопросов.

        Аргументы:
            request: HTTP-запрос.

        Возвращает:
            Response: Ответ с данными всех вопросов.
        """
        queryset = self.get_queryset()
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)

    def retrieve(self, request, *args, **kwargs):
        """
        Получение информации о конкретном вопросе.

        Аргументы:
            request: HTTP-запрос.

        Возвращает:
            Response: Ответ с данными конкретного вопроса.
        """
        instance = self.get_object()
        serializer = self.get_serializer(instance)
        return Response(serializer.data)

    def update(self, request, *args, **kwargs):
        """
        Обновление информации о вопросе.

        Аргументы:
            request: HTTP-запрос с данными для обновления.

        Возвращает:
            Response: Ответ с обновленными данными вопроса.
        """
        partial = kwargs.pop("partial", False)
        instance = self.get_object()  # Получаем существующий вопрос
        serializer = self.get_serializer(instance, data=request.data, partial=partial)
        serializer.is_valid(raise_exception=True)
        self.perform_update(serializer)  # Обновляем вопрос

        # Обновляем ответы
        answers_data = request.data.get("answers", [])
        existing_answers = {answer.id: answer for answer in instance.answers.all()}

        for answer_data in answers_data:
            answer_id = answer_data.get("id")
            if answer_id in existing_answers:
                # Обновляем существующий ответ
                answer = existing_answers[answer_id]
                answer.answer_text = answer_data.get("answer_text", answer.answer_text)
                answer.is_correct = answer_data.get("is_correct", answer.is_correct)
                answer.save()
            else:
                # Если ID не существует, создаем новый ответ
                Answer.objects.create(
                    question=instance,
                    answer_text=answer_data["answer_text"],
                    is_correct=answer_data["is_correct"],
                )

        # Удаляем ответы, которые не были переданы в запросе
        for answer in instance.answers.all():
            if answer.id not in [ans["id"] for ans in answers_data]:
                answer.delete()

        return Response(serializer.data)

    def destroy(self, request, *args, **kwargs):
        """
        Удаление вопроса.

        Аргументы:
            request: HTTP-запрос.

        Возвращает:
            Response: Ответ со статусом 204 (Нет содержимого).
        """
        instance = self.get_object()
        self.perform_destroy(instance)
        return Response(status=status.HTTP_204_NO_CONTENT)


class TestResultViewSet(viewsets.ViewSet):
    """
    ViewSet для управления результатами тестов пользователей.

    Доступные действия:
        - list: Получить список результатов тестов текущего пользователя.
        - retrieve: Получить информацию о конкретном результате теста.
        - list_by_user: Получить результаты тестов для указанного пользователя.
    """

    def get_permissions(self):
        if self.request.method in ["POST", "PUT", "PATCH", "DELETE"]:
            # Разрешить доступ только администраторам или владельцам
            self.permission_classes = [IsAdminOrOwner]
        else:
            # Все аутентифицированные пользователи могут просматривать
            self.permission_classes = [IsAuthenticatedForRead]
        return super().get_permissions()

    def list(self, request):
        """
        Получение списка результатов тестов текущего пользователя.

        Аргументы:
            request: HTTP-запрос.

        Возвращает:
            Response: Ответ с данными всех результатов тестов текущего пользователя.
        """
        user_results = TestResult.objects.filter(user=request.user)
        serializer = TestResultSerializer(user_results, many=True)
        return Response(serializer.data)

    def retrieve(self, request, pk=None):
        """
        Получение информации о конкретном результате теста.

        Аргументы:
            request: HTTP-запрос.
            pk: Уникальный идентификатор результата теста.

        Возвращает:
            Response: Ответ с данными конкретного результата теста или ошибка, если результат не найден.
        """
        try:
            result = TestResult.objects.get(pk=pk, user=request.user)
            serializer = TestResultSerializer(result)
            return Response(serializer.data)
        except TestResult.DoesNotExist:
            return Response(
                {"error": "Результат не найден."}, status=status.HTTP_404_NOT_FOUND
            )

    def list_by_user(self, request, user_id=None):
        """
        Получение результатов тестов для указанного пользователя.

        Аргументы:
            request: HTTP-запрос.
            user_id: Уникальный идентификатор пользователя.

        Возвращает:
            Response: Ответ с данными результатов тестов указанного пользователя или ошибка доступа.
        """
        if request.user.id != user_id:
            return Response(
                {"error": "У вас нет доступа к результатам этого пользователя."},
                status=status.HTTP_403_FORBIDDEN,
            )

        user_results = TestResult.objects.filter(user_id=user_id)
        serializer = TestResultSerializer(user_results, many=True)
        return Response(serializer.data)
