from django.urls import path
from . import views

urlpatterns = [
    path("", views.homePageRedirect, name="redirect"),
    path('clock/adduser/', views.adduser, name="adduser"),
    path('clock/', views.homePage, name="index")
]
