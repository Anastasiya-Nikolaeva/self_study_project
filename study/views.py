import logging
from rest_framework import viewsets, status
from django.core.exceptions import ObjectDoesNotExist
from rest_framework.response import Response



from users.permissions import IsAdmin, IsOwner, IsAuthenticatedUser

from .models import Material, Question, Review, Test, Theme, Answer
from .serializers import (
    MaterialSerializer,
    QuestionSerializer,
    ReviewSerializer,
    TestSerializer,
    ThemeSerializer, CheckAnswersSerializer,
)


logger = logging.getLogger(__name__)

class ThemeViewSet(viewsets.ModelViewSet):
    queryset = Theme.objects.all()
    serializer_class = ThemeSerializer
    permission_classes = [IsAdmin | IsOwner]


class MaterialViewSet(viewsets.ModelViewSet):
    queryset = Material.objects.all()
    serializer_class = MaterialSerializer
    permission_classes = [IsAdmin | IsOwner]


class ReviewViewSet(viewsets.ModelViewSet):
    queryset = Review.objects.all()
    serializer_class = ReviewSerializer
    permission_classes = [IsAdmin | IsOwner]


class TestViewSet(viewsets.ModelViewSet):
    queryset = Test.objects.all()
    serializer_class = TestSerializer

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)

class QuestionViewSet(viewsets.ModelViewSet):
    queryset = Question.objects.all()
    serializer_class = QuestionSerializer

    def create(self, request, *args, **kwargs):
        # Сначала валидируем и сохраняем вопрос
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        question = serializer.save()

        # Теперь обрабатываем варианты ответов
        answers_data = request.data.get('answers', [])
        for answer_data in answers_data:
            Answer.objects.create(
                question=question,
                answer_text=answer_data['answer_text'],
                is_correct=answer_data['is_correct']
            )

        # Возвращаем данные вопроса с вариантами ответов
        return Response(serializer.data, status=status.HTTP_201_CREATED)

class AnswerCheckViewSet(viewsets.ViewSet):

    def create(self, request, test_id):
        try:
            test = Test.objects.get(id=test_id)
        except ObjectDoesNotExist:
            return Response({"error": "Test not found."}, status=status.HTTP_404_NOT_FOUND)

        serializer = CheckAnswersSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        correct_answers = 0
        total_questions = test.questions.count()

        for question in test.questions.all():
            user_answer_ids = serializer.validated_data['answers'].get(str(question.id), [])
            correct_answer_ids = question.answers.filter(is_correct=True).values_list('id', flat=True)

            logger.info(
                f"Question ID: {question.id}, User Answers: {user_answer_ids}, Correct Answers: {list(correct_answer_ids)}"
            )

            # Преобразование ответов в нижний регистр для сравнения
            user_answer_ids_lower = {str(answer_id).lower() for answer_id in user_answer_ids}
            correct_answer_ids_lower = {str(answer_id).lower() for answer_id in correct_answer_ids}

            # Проверка, совпадают ли ответы пользователя с правильными ответами
            if user_answer_ids_lower == correct_answer_ids_lower:
                correct_answers += 1

        score = (correct_answers / total_questions) * 100 if total_questions > 0 else 0
        return Response({'score': score}, status=status.HTTP_200_OK)
