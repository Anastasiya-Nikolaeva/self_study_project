from django.urls import include, path

from .views import (
    MaterialViewSet,
    QuestionViewSet,
    ReviewViewSet,
    TestViewSet,
    ThemeViewSet, AnswerCheckViewSet,
)

app_name = "study"

urlpatterns = [
    path('themes/', ThemeViewSet.as_view({'get': 'list', 'post': 'create'}), name='theme-list'),
    path('themes/<int:pk>/', ThemeViewSet.as_view({'get': 'retrieve', 'put': 'update', 'patch': 'update', 'delete': 'destroy'}), name='theme-detail'),

    path('materials/', MaterialViewSet.as_view({'get': 'list', 'post': 'create'}), name='material-list'),
    path('materials/<int:pk>/', MaterialViewSet.as_view({'get': 'retrieve', 'put': 'update', 'patch': 'update', 'delete': 'destroy'}), name='material-detail'),

    path('reviews/', ReviewViewSet.as_view({'get': 'list', 'post': 'create'}), name='review-list'),
    path('reviews/<int:pk>/', ReviewViewSet.as_view({'get': 'retrieve', 'put': 'update', 'patch': 'update', 'delete': 'destroy'}), name='review-detail'),

    path('tests/', TestViewSet.as_view({'get': 'list', 'post': 'create'}), name='test-list'),
    path('tests/<int:pk>/', TestViewSet.as_view({'get': 'retrieve', 'put': 'update', 'patch': 'update', 'delete': 'destroy'}), name='test-detail'),

    path('questions/', QuestionViewSet.as_view({'get': 'list', 'post': 'create'}), name='question-list'),
    path('questions/<int:pk>/', QuestionViewSet.as_view({'get': 'retrieve', 'put': 'update', 'patch': 'update', 'delete': 'destroy'}), name='question-detail'),

    path('check-answers/<int:test_id>/', AnswerCheckViewSet.as_view({'post': 'create'}), name='check-answers'),
]