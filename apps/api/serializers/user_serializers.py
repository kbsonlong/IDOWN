# -*- coding: utf-8 -*-
# @Time    : 2019-07-29 18:05
# @Author  : kbsonlong
# @Email   : kbsonlong@gmail.com
# @Blog    : www.alongparty.cn
# @File    : user_serializers.py
# @Software: PyCharm
from rest_framework import serializers
from django.contrib.auth.models import Group,Permission

from accounts.models import UserProfile,UserLog
from assets import models


class UsersSerializer(serializers.ModelSerializer):
    """
    用户管理
    """
    class Meta:
        model = UserProfile
        fields = ('id', 'username', 'mobile', 'is_superuser', 'is_active', 'groups', 'user_permissions','image')



class PermissionSerializer(serializers.ModelSerializer):
    """
    权限管理
    """
    class Meta:
        model = Permission
        fields = ('id', 'name')


class GroupSerializer(serializers.ModelSerializer):
    """
    用户组管理
    """
    class Meta:
        model = Group
        fields = ('id', 'name', 'user_set', 'permissions')


class UserLogSerializer(serializers.ModelSerializer):
    """
    用户操作记录
    """
    class Meta:
        model = UserLog
        fields = '__all__'

