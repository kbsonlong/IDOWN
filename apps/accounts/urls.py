# -*- coding: utf-8 -*-
# @Time    : 2019-07-29 17:07
# @Author  : kbsonlong
# @Email   : kbsonlong@gmail.com
# @Blog    : www.alongparty.cn
# @File    : urls.py
# @Software: PyCharm


from django.urls import path
from accounts import views

app_name = 'accounts'
urlpatterns = [
    path('login/',views.user_login,name = 'login'),
    path('logout/',views.user_logout,name = 'logout'),
    path('user_list/',views.UserListView.as_view(),name = 'user_list'),
    path('group_list/',views.GroupListView.as_view(),name = 'group_list'),
    path('create_user/',views.UserListView.as_view(),name = 'create_user'),
    path('reset_password/<int:pk>/',views.reset_password,name = 'reset_password'),
]
