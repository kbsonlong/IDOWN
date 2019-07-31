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
from rest_framework.documentation import include_docs_urls

app_name = 'api'

API_TITLE = 'API Documents'
API_DESCRIPTION = 'API Information'

router = routers.DefaultRouter()
##用户权限认证
router.register(r'account/users', user_views.UsersViewSet)
router.register(r'account/permission', user_views.PermissionViewSet)
router.register(r'account/group', user_views.GroupViewSet)
router.register(r'account/user_log', user_views.UserLogViewSet)

##资产管理
router.register(r'assets',asset_views.AssetsViewSet)
router.register(r'asset/server',asset_views.ServerViewSet)
router.register(r'asset/idc',asset_views.IdcViewSet)
router.register(r'asset/businessunit',asset_views.BusinessUnitViewSet)
router.register(r'asset/env',asset_views.EnvsViewSet)
router.register(r'asset/apps',asset_views.AppViewSet)



urlpatterns = [
    path(r'', include(router.urls)),
    path(r'api/', include('rest_framework.urls', namespace='rest_framework')),
    # 接口文档路由
    path(r'docs/', include_docs_urls(title='My API title')),
    # path(r'docs/', include_docs_urls(title=API_TITLE, description=API_DESCRIPTION, authentication_classes=[], permission_classes=[])),
]