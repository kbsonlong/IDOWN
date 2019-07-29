from django.shortcuts import render
from rest_framework import viewsets, permissions
from api.serializers import *
# Create your views here.


class UsersViewSet(viewsets.ModelViewSet):
    queryset = UserProfile.objects.all().order_by('id')
    serializer_class = UsersSerializer
    permission_classes = (permissions.IsAuthenticated,)


class PermissionViewSet(viewsets.ModelViewSet):
    queryset = Permission.objects.all().order_by('id')
    serializer_class = PermissionSerializer
    permission_classes = (permissions.IsAuthenticated,)


class GroupViewSet(viewsets.ModelViewSet):
    queryset = Group.objects.all().order_by('id')
    serializer_class = GroupSerializer
    permission_classes = (permissions.IsAuthenticated,)


class UserLogViewSet(viewsets.ModelViewSet):
    queryset = UserLog.objects.all().order_by('id')
    serializer_class = UserLogSerializer
    permission_classes = (permissions.IsAuthenticated,)