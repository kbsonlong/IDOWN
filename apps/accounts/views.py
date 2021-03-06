from django.shortcuts import render,redirect
from django.http import HttpResponse,HttpResponseRedirect,JsonResponse
from django.views.generic import ListView,DetailView
from django.views.generic.edit import UpdateView
from django.contrib.auth import authenticate,login,logout
from django.contrib.auth.hashers import make_password
from django.contrib.auth.decorators import login_required,permission_required
from django.utils.decorators import method_decorator
from django.contrib.auth.models import Group
# Create your views here.

from accounts import models
from accounts.forms import UserLoginForm


def user_login(request):
    """
    用户登录
    :param request:
    :return:
    """
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
    models.UserProfile.objects.filter(username=request.user).update(
        login_status=1
    )
    logout(request)
    return HttpResponseRedirect('/accounts/login/')



@method_decorator(login_required,name="dispatch")
class UserListView(ListView):
    """
    用户列表
    """
    model = models.UserProfile
    template_name = "accounts/user_list.html"
    context_object_name = "user_list"


@permission_required('accounts.change_userprofile', raise_exception=True)
def reset_password(request, pk):
    """
    重置密码
    :param request:
    :param pk:
    :return:
    """
    if request.method == 'POST':
        try:
            models.UserProfile.objects.filter(id=pk).update(
                password=make_password('123456')
            )

            return JsonResponse({"code": 200, "data": None, "msg": "密码重置成功！密码为123456"})
        except Exception as e:
            return JsonResponse({"code": 500, "data": None, "msg": "密码重置失败，原因：{}".format(e)})


@method_decorator(login_required,name="dispatch")
class GroupListView(ListView):
    """
    用户组列表
    """
    model = Group
    template_name = "accounts/group_list.html"
    context_object_name = "group_list"


@method_decorator(login_required,name="dispatch")
class UserDetailView(DetailView):
    model = models.UserProfile
    template_name = "accounts/user_profile.html"
    context_object_name = "user"
    pk_url_kwarg = "pk"


    def get_context_data(self, **kwargs):
        context = super(UserDetailView,self).get_context_data(**kwargs)
        user = models.UserProfile.objects.get(username=self.request.user)
        # my_plans = user.self_user.filter(status=0) | user.attention_user.filter(status=0)
        my_plans = user.self_user.all() | user.attention_user.all()
        context.update({'my_plans':my_plans})
        return context


def create_plan(request):
    if request.method == 'POST':
        try:
            user_plan = models.UserPlan.objects.create(
                user=models.UserProfile.objects.get(id=request.POST.get('user')),
                title=request.POST.get('title'),
                content=request.POST.get('content'),
                start_time=request.POST.get('start_time'),
                end_time=request.POST.get('end_time'),
            )
            attention = request.POST.getlist('attention')
            if attention:
                user_plan.attention.set(attention)
            return JsonResponse({'code': 200, 'result': True, 'msg': '数据保存成功！'})
        except Exception as e:
            return JsonResponse({'code': 500, 'result': False, 'msg': '数据保存失败！{}'.format(e)})
    users = models.UserProfile.objects.exclude(id__in=[request.user.id])
    return render(request, 'accounts/create_plan.html', locals())


def plan_info(request, pk):
    user_plan = models.UserPlan.objects.prefetch_related('attention').get(id=pk)
    if request.method == 'GET':
        users = models.UserProfile.objects.exclude(id__in=[request.user.id])
        return render(request, 'accounts/plan_info.html', locals())
    elif request.method == 'POST':
        try:
            user_plan.status = 1 if request.POST.get('status') else 0
            user_plan.title = request.POST.get('title')
            user_plan.content = request.POST.get('content')
            user_plan.start_time = request.POST.get('start_time')
            user_plan.end_time = request.POST.get('end_time')
            attention = request.POST.getlist('attention')
            if attention:
                user_plan.attention.set(attention)
            else:
                user_plan.attention.clear()
            user_plan.save()
            return JsonResponse({'code': 200, 'result': True, 'msg': '数据保存成功！'})
        except Exception as e:
            return JsonResponse({'code': 500, 'result': False, 'msg': '数据保存失败！{}'.format(e)})
    elif request.method == 'DELETE':
        try:
            user_plan.delete()
            return JsonResponse({'code': 200, 'result': True, 'msg': '数据删除成功！'})
        except Exception as e:
            return JsonResponse({'code': 500, 'result': False, 'msg': '数据删除失败！{}'.format(e)})