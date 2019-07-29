from django.shortcuts import render,redirect
from django.http import HttpResponse,HttpResponseRedirect
from django.views.generic import ListView
from django.contrib.auth import authenticate,login,logout
from django.contrib.auth.decorators import login_required,permission_required
# Create your views here.

from accounts import models
from accounts.forms import UserLoginForm


def user_login(request):
    next_url = request.GET.get('next')
    context = {'next': next_url}
    if request.method == 'POST':
        user_login_form = UserLoginForm(data=request.POST)
        remember_me = request.POST.get('remember_me')
        if user_login_form.is_valid():
            ##.cleaned_data清洗出合法数据
            data = user_login_form.cleaned_data
            user = authenticate(username=data['username'], password=data['password'])
            if user and user.is_active:
                # 将用户数据保存在session中
                login(request, user)
                request.session['username'] = data['username']
                if remember_me:
                    ##选择记住，session过期时间为7天
                    request.session.set_expiry(60 * 60 * 24 * 7)
                    # request.session.set_expiry(60)
                else:
                    ##session默认一小时过期
                    request.session.set_expiry(60 * 60)
                print(request.POST)
                next_url = request.POST.get('next')
                if next_url:
                    return HttpResponseRedirect(request.POST.get('next'))
                else:
                    return redirect("/")
            else:
                context.update({"error": "账号或密码输入错误，请重新输入"})
        else:
            context.update({"error": "账号或密码输入不合法，请重新输入"})
    elif request.method == 'GET':
        if request.session.get('username') and request.session.get('lock'):
            del request.session['lock']
            del request.session['username']
        user_login_form = UserLoginForm()
        context.update({'form': user_login_form})
    else:
        context.update({"error": "请使用GET或者POST请求"})
    return render(request, 'accounts/login1.html', context)

def user_logout(request):
    logout(request)
    return redirect("accounts:login")


@login_required
def index(request):
    return render(request,'base/base.html')



class UserListView(ListView):
    model = models.UserProfile
    template_name = "accounts/user_list.html"
    context_object_name = "user_list"