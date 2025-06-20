# from django.urls import path
from chat import consumers
from django.urls import re_path

websocket_urlpatterns = [
    re_path(r'chat/$', consumers.ChatConsumer.as_asgi()),
    # re_path(r'ws/signaling/$', consumers.SignalingConsumer.as_asgi()),
]