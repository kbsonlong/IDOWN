# -*- coding: utf-8 -*-
# @Time    : 2019-07-30 14:24
# @Author  : kbsonlong
# @Email   : kbsonlong@gmail.com
# @Blog    : www.alongparty.cn
# @File    : asset_serializers.py
# @Software: PyCharm
from rest_framework import serializers

from assets import models

class AssetSerializer(serializers.ModelSerializer):
    """
    资产列表
    """
    class Meta:
        model = models.Asset
        fields = '__all__'


class ServerSerializer(serializers.ModelSerializer):
    """
    服务器管理
    """
    class Meta:
        model = models.Server
        fields = '__all__'

class EnvSerializer(serializers.ModelSerializer):
    """
    运行环境管理
    """
    class Meta:
        model = models.Env
        fields = '__all__'


class IdcSerializer(serializers.ModelSerializer):
    """
    机房序列化
    """
    class Meta:
        model = models.IDC
        fields = '__all__'

class BusinessUnitSerializer(serializers.ModelSerializer):
    """
    业务线
    """
    class Meta:
        model = models.BusinessUnit
        fields = '__all__'

class AppSerializer(serializers.ModelSerializer):
    """
    I应用管理
    """
    class Meta:
        model = models.App
        fields = '__all__'