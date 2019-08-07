from django.urls import path,re_path

# from . import websocket
from .webssh import SSHConsumer

websocket_urlpatterns = [
    # path('webssh/', websocket.WebSSH),
    re_path(r'ws/([0-9]+)/(?P<group_name>.*)/', SSHConsumer),
]