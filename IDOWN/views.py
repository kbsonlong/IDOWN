# -*- coding: utf-8 -*-
# @Time    : 2019-07-29 16:22
# @Author  : kbsonlong
# @Email   : kbsonlong@gmail.com
# @Blog    : www.alongparty.cn
# @File    : views.py
# @Software: PyCharm
from django.shortcuts import render,render_to_response
from django.contrib.auth.decorators import login_required


@login_required
def dashboard(request):
    return render(request,'base/dashboard.html')


def page_forbidden(request, exception):
    print(request.user.id)
    response = render_to_response("base/403.html", locals())
    response.status_code = 403
    return response

def page_not_found(request, exception):
    print(request.user.id)
    response = render_to_response("base/404.html", locals())
    response.status_code = 404
    return response

def page_error(request):
    response = render_to_response("base/500.html", locals())
    response.status_code = 500
    return response