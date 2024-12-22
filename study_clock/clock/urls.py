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
from .views import ProtectedView, VerifyEmailView, UpdateEmailView, UpdateAvatarView, \
    MessageHistoryView, SendMessageView, UpdateActivityView, CreateActivityView, DeleteActivityView, \
    GetActivitiesListView, UserReadView, TimerUpdate
from .views import ProtectedView, UserUpdateView, VerifyEmailView, UpdateEmailView, UpdateAvatarView, \
    MessageHistoryView, SendMessageView
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
    path('clock/login/', views.LoginView.as_view(), name='login'),
    #path('clock/login/', views.login_page, name='login'),
    path('api/', include(router.urls)),
    path('api/users/custom/update/<int:pk>/', UserUpdateView.as_view(), name='user-update'),
    path('api/users/custom/read/', UserReadView.as_view(), name='user-read'),
    path('verify-email/', VerifyEmailView.as_view(), name='verify-email'),
    path('update-email/', UpdateEmailView.as_view(), name='update-email'),
    path('update-avatar/', UpdateAvatarView.as_view(), name='update-avatar'),
    path('chat/messages/<int:user_id>/', MessageHistoryView.as_view(), name='message-history'),
    path('chat/send/', SendMessageView.as_view(), name='send-message'),
    # path('chat/', views.chat_view, name='chat'),
    path('api/activity/update/', UpdateActivityView.as_view(), name='update-activity'),
    path('api/activity/create/', CreateActivityView.as_view(), name='create-activity'),
    path('api/activity/delete/', DeleteActivityView.as_view(), name='delete-activity'),
    path('api/activity/all/', GetActivitiesListView.as_view(), name='all-activities'),
    path('api/timer/add-time/', TimerUpdate.as_view(), name='add-time')
]
