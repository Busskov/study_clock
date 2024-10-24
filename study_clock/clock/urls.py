from django.urls import path
from . import views
from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView
)

from .protected_view import ProtectedView
from .register_view import RegisterView

urlpatterns = [
    path("", views.homePageRedirect, name="redirect"),
    path('clock/adduser/', views.adduser, name="adduser"),
    path('clock/', views.homePage, name="index"),
    path('clock/token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('clock/token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('clock/register/', RegisterView.as_view(), name='register'),
    path('clock/protected/', ProtectedView.as_view(), name='protected_view')
]
