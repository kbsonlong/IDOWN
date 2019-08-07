# -*- coding: utf-8 -*-
# @Time    : 2019-07-14 20:28
# @Author  : kbsonlong
# @Email   : kbsonlong@gmail.com
# @Blog    : www.alongparty.cn
# @File    : urls.py
# @Software: PyCharm
from django.urls import path,re_path
from . import views

app_name = 'webssh'
urlpatterns = [
    path('', views.index,name='index'),
    path('web_ssh/<int:pk>/', views.get_info,name='web_ssh'),
    path('upload_ssh_key/', views.upload_ssh_key,name='upload_ssh_key'),
    path('login_record/', views.login_fort_record,name='login_record'),
    re_path(r'record_play/(?P<pk>[0-9]+)/', views.record_play, name='record_play'),
    re_path(r'ssh/(?P<pk>[0-9]+)/', views.ssh_terminal, name='ssh_terminal'),
]
