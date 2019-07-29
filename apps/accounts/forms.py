# -*- coding: utf-8 -*-
# @Time    : 2019-07-29 16:44
# @Author  : kbsonlong
# @Email   : kbsonlong@gmail.com
# @Blog    : www.alongparty.cn
# @File    : forms.py
# @Software: PyCharm

from django import forms
from .models import UserProfile

class UserLoginForm(forms.Form):
    username = forms.CharField()
    password = forms.CharField()