from django.urls import path, re_path, include
from drf_yasg import openapi
from rest_framework import permissions
from drf_yasg.views import get_schema_view
from rest_framework.routers import DefaultRouter

from . import views
from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView
)
from .views import ProtectedView, UserUpdateView
from .views import RegisterView

schema_view = get_schema_view(
    openapi.Info(
        title='Clock API',
        default_version='v1',
        description='API documentation for the Clock application',
        contact=openapi.Contact(email='bus9ko@gmail.com')
    ),
    public=True,
    permission_classes=[permissions.AllowAny],
)

router = DefaultRouter()
router.register(r'users', views.UserFilterViewSet, basename='user')

urlpatterns = [
    path("", views.homePageRedirect, name="redirect"),
    path('clock/', views.homePage, name="index"),
    path('clock/token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('clock/token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('clock/register/', RegisterView.as_view(), name='register'),
    path('clock/protected/', ProtectedView.as_view(), name='protected_view'),
    re_path(r'^swagger(?P<format>\.json|\.yaml)$', schema_view.without_ui(cache_timeout=0), name='schema-json'),
    path('swagger/', schema_view.with_ui('swagger', cache_timeout=0), name='schema-swagger-ui'),
    path('redoc/', schema_view.with_ui('redoc', cache_timeout=0), name='schema-redoc'),
    path('chat/', views.chat_view, name='chat'),
    # path('clock/login/', views.LoginView.as_view(), name='login'),
    path('clock/login/', views.login_page, name='login'),
    path('api/', include(router.urls)),
    path('api/users/<int:pk>/', UserUpdateView.as_view(), name='user-update')
]
