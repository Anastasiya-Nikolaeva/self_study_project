from django.contrib import admin
from django.urls import include, path
from rest_framework_simplejwt.views import TokenObtainPairView

urlpatterns = [
    path("admin/", admin.site.urls),
    path("users/", include("users.urls")),
    path("study/", include("study.urls")),
    path('api/token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
]
