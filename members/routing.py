from django.urls import re_path
from . import consumers

websocket_urlpatterns = [
    re_path(r'ws/user_status/$', consumers.UserStatusConsumer.as_asgi()),
    re_path(r'ws/echo/$', consumers.EchoConsumer.as_asgi()),  # Test endpoint
    re_path(r'ws/tasks/$', consumers.TaskManagerConsumer.as_asgi()),  # New general updates endpoint
]
