# -*- coding: utf-8 -*-
# @Time    : 2019-08-07 10:37
# @Author  : kbsonlong
# @Email   : kbsonlong@gmail.com
# @Blog    : www.alongparty.cn
# @File    : routing.py
# @Software: PyCharm

import os
from channels.auth import AuthMiddlewareStack
from channels.routing import ProtocolTypeRouter, URLRouter

from webssh.channel import routing


os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'IDOWN.settings')

application = ProtocolTypeRouter({
    'websocket': AuthMiddlewareStack(
        URLRouter(
            routing.websocket_urlpatterns
        )
    ),
})