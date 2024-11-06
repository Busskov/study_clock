from django.urls import re_path

websocket_urlpatterns = [
    re_path(r'ws/support/$', consumers.ChatConsumer.as_asgi()),
]