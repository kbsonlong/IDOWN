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
from api.views import asset_views

app_name = 'api'

router = routers.DefaultRouter()
router.register(r'users', user_views.UsersViewSet)
router.register(r'permission', user_views.PermissionViewSet)
router.register(r'group', user_views.GroupViewSet)
router.register(r'user_log', user_views.UserLogViewSet)

##资产管理
router.register(r'assets',asset_views.AssetsViewSet)
router.register(r'server',asset_views.ServerViewSet)
router.register(r'idc',asset_views.IdcViewSet)
router.register(r'businessunit',asset_views.BusinessUnitViewSet)
router.register(r'env',asset_views.EnvsViewSet)






urlpatterns = [
    path(r'', include(router.urls)),
    path(r'api/', include('rest_framework.urls', namespace='rest_framework'))
]