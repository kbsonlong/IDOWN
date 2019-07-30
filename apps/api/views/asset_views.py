# -*- coding: utf-8 -*-
# @Time    : 2019-07-30 14:15
# @Author  : kbsonlong
# @Email   : kbsonlong@gmail.com
# @Blog    : www.alongparty.cn
# @File    : asset_views.py
# @Software: PyCharm
from rest_framework import viewsets, permissions

from api.serializers.asset_serializers import *
from assets import models


class AssetsViewSet(viewsets.ModelViewSet):
    """
    资产管理
    """
    queryset = models.Asset.objects.all().order_by('id')
    serializer_class = AssetSerializer
    permission_classes = (permissions.IsAuthenticated,)



class ServerViewSet(viewsets.ModelViewSet):
    """
    服务器列表
    """
    queryset = models.Server.objects.all().order_by('id')
    serializer_class = ServerSerializer
    permission_classes = (permissions.IsAuthenticated,)


class EnvsViewSet(viewsets.ModelViewSet):
    """
    环境列表
    """
    queryset = models.Env.objects.all().order_by('id')
    serializer_class = EnvSerializer
    permission_classes = (permissions.IsAuthenticated,)


class IdcViewSet(viewsets.ModelViewSet):
    """
    机房列表
    """
    queryset = models.IDC.objects.all().order_by('id')
    serializer_class = IdcSerializer
    permission_classes = (permissions.IsAuthenticated,)

class BusinessUnitViewSet(viewsets.ModelViewSet):
    """
    业务线管理
    """
    queryset = models.BusinessUnit.objects.all().order_by('id')
    serializer_class = BusinessUnitSerializer
    permission_classes = (permissions.IsAuthenticated,)