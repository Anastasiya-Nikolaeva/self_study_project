from django.urls import path

from users.apps import UsersConfig

from .views import (AnswerViewSet, MaterialViewSet, QuestionViewSet,
                    ReviewViewSet, TestResultViewSet, TestViewSet,
                    ThemeViewSet)

app_name = UsersConfig.name

urlpatterns = [
    path(
        "themes/",
        ThemeViewSet.as_view({"get": "list", "post": "create"}),
        name="theme-list",
    ),
    path(
        "themes/<int:pk>/",
        ThemeViewSet.as_view(
            {"get": "retrieve", "put": "update", "patch": "update", "delete": "destroy"}
        ),
        name="theme-detail",
    ),
    path(
        "materials/",
        MaterialViewSet.as_view({"get": "list", "post": "create"}),
        name="material-list",
    ),
    path(
        "materials/<int:pk>/",
        MaterialViewSet.as_view(
            {"get": "retrieve", "put": "update", "patch": "update", "delete": "destroy"}
        ),
        name="material-detail",
    ),
    path(
        "reviews/",
        ReviewViewSet.as_view({"get": "list", "post": "create"}),
        name="review-list",
    ),
    path(
        "reviews/<int:pk>/",
        ReviewViewSet.as_view(
            {"get": "retrieve", "put": "update", "patch": "update", "delete": "destroy"}
        ),
        name="review-detail",
    ),
    path(
        "tests/",
        TestViewSet.as_view({"get": "list", "post": "create"}),
        name="test-list",
    ),
    path(
        "tests/<int:pk>/",
        TestViewSet.as_view(
            {"get": "retrieve", "put": "update", "patch": "update", "delete": "destroy"}
        ),
        name="test-detail",
    ),
    path(
        "questions/",
        QuestionViewSet.as_view({"get": "list", "post": "create"}),
        name="question-list",
    ),
    path(
        "questions/<int:pk>/",
        QuestionViewSet.as_view(
            {"get": "retrieve", "put": "update", "patch": "update", "delete": "destroy"}
        ),
        name="question-detail",
    ),
    path(
        "answers/check/",
        AnswerViewSet.as_view({"post": "check_answer"}),
        name="check-answer",
    ),
    path(
        "test/results/",
        TestResultViewSet.as_view({"get": "list"}),
        name="test-result-list",
    ),
    path(
        "test/results/user/<int:user_id>/",
        TestResultViewSet.as_view({"get": "list_by_user"}),
        name="test-result-list-by-user",
    ),
]
