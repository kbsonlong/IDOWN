# -*- coding: utf-8 -*-
# @Time    : 2019-07-29 18:12
# @Author  : kbsonlong
# @Email   : kbsonlong@gmail.com
# @Blog    : www.alongparty.cn
# @File    : urls.py
# @Software: PyCharm


from django.urls import path, include
from rest_framework import routers
from api.views import user_views


app_name = 'api'

router = routers.DefaultRouter()
router.register(r'users', user_views.UsersViewSet)
router.register(r'permission', user_views.PermissionViewSet)
router.register(r'group', user_views.GroupViewSet)
router.register(r'user_log', user_views.UserLogViewSet)

urlpatterns = [
    path(r'', include(router.urls)),
    path(r'api/', include('rest_framework.urls', namespace='rest_framework'))
]