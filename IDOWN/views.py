# -*- coding: utf-8 -*-
# @Time    : 2019-07-29 16:22
# @Author  : kbsonlong
# @Email   : kbsonlong@gmail.com
# @Blog    : www.alongparty.cn
# @File    : views.py
# @Software: PyCharm
from django.shortcuts import render
from django.contrib.auth.decorators import login_required


@login_required
def dashboard(request):
    return render(request,'base/dashboard.html')