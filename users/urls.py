from django.urls import include, path
from rest_framework.routers import DefaultRouter
from rest_framework_simplejwt.views import (TokenObtainPairView,
                                            TokenRefreshView)

from .views import CustomUserViewSet

app_name = "users"

router = DefaultRouter()

urlpatterns = [
    path("token/", TokenObtainPairView.as_view(), name="token_obtain_pair"),
    path("token/refresh/", TokenRefreshView.as_view(), name="token_refresh"),
    path("users/", CustomUserViewSet.as_view({'get': 'list', 'post': 'create'}), name='customuser-list'),
    path("users/<int:pk>/", CustomUserViewSet.as_view({'get': 'retrieve', 'put': 'update', 'patch': 'partial_update', 'delete': 'destroy'}), name='customuser-detail'),
]
