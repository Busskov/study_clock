from django.urls import path
from . import views
from .views import (
    UserListApiView,
)

urlpatterns = [
    path("", views.homePageRedirect, name="redirect"),
    path('clock/adduser/', views.adduser, name="adduser"),
    path('clock/', views.homePage, name="index"),
    path('clock/api', UserListApiView.as_view())
]
