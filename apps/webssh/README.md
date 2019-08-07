---
title: README
tags:
  - webssh
  - 自动化运维
categories:
  - 自动化运维
date: 2019-07-14 20:38
status: publish
comment_status: open
Blog: https://www.alongparty.cn
Email: kbsonlong@gmail.com
Author: kbsonlong
---

## 依赖包
```bash
pip install channels==2.0.2 paramiko

##windows需要安装pywin32
pip install pywin32

```

## 配置
### settings.py
```python
INSTALL_APPS =[
    ...
    'channels',
    'webssh',
]


ASGI_APPLICATION = '<PROJECT_NAME>.routing.application'

######################################
# 上传文件配置
######################################
MEDIA_URL = '/media/'
MEDIA_ROOT = os.path.join(BASE_DIR, 'media')

```

### routing.py
```python
from channels.auth import AuthMiddlewareStack
from channels.routing import ProtocolTypeRouter, URLRouter

from webssh.channel import routing

application = ProtocolTypeRouter({
    'websocket': AuthMiddlewareStack(
        URLRouter(
            routing.websocket_urlpatterns
        )
    ),
})
```

### 配置 urls.py
```python
path('webssh/',include('webssh.urls',namespace='webssh')),
```
> 需按照以上配置
