# -*- coding: utf-8 -*-
# @Time    : 2019-07-29 18:05
# @Author  : kbsonlong
# @Email   : kbsonlong@gmail.com
# @Blog    : www.alongparty.cn
# @File    : serializers.py
# @Software: PyCharm
from rest_framework import serializers
from django.contrib.auth.models import Group,Permission
from accounts.models import UserProfile,UserLog

class UsersSerializer(serializers.ModelSerializer):

    class Meta:
        model = UserProfile
        fields = ('id', 'username', 'mobile', 'is_superuser', 'is_active', 'groups', 'user_permissions')



class PermissionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Permission
        fields = ('id', 'name')


class GroupSerializer(serializers.ModelSerializer):
    class Meta:
        model = Group
        fields = ('id', 'name', 'user_set', 'permissions')


class UserLogSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserLog
        fields = '__all__'