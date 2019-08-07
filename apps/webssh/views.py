import os
import json
import datetime
# Create your views here.
from django.shortcuts import render, HttpResponse,HttpResponseRedirect
from django.conf import settings
from django.contrib.auth.decorators import login_required,permission_required
from django.http import JsonResponse, FileResponse
from django.contrib.auth import get_user_model


from .models import SshUser,FortRecord
from assets.models import Asset
from .channel.websftp import SFTP


User = get_user_model()

@login_required
def index(request):
    user = SshUser.objects.filter(username=request.user)

    return render(request, 'index.html')

def get_info(request,pk):
    asset = Asset.objects.filter(pk=pk)
    user = SshUser.objects.get(username=request.user)

    ret = {}
    try:
        if user:
            ip = asset[0].server.i_ip
            if ip:
                ip= ip
            else:
                ip = asset[0].server.local_ip
            username = user.username
            password = user.password
            ssh_key = user.ssh_key
            if user.is_key:
                auth = 'key'
            else:
                auth = ''
            ret = {"username": username, 'password': password, 'ssh_key': ssh_key, 'auth': auth, 'ip': ip, 'port': 22,
                   "static": True}
        else:
            return HttpResponseRedirect('/webssh/',locals())
    except Exception as e:
        ret['status'] = False
        ret['error'] = '请求错误,{}'.format(e)
    finally:

        return HttpResponse(json.dumps(ret))

def upload_ssh_key(request):
    if request.method == 'POST':

        username = request.POST.get('user')
        password = request.POST.get('password')
        pkey = request.FILES.get('pkey')
        auth = request.POST.get('auth')
        user = User.objects.filter(username=username).first()

        if user :
            sshuser = SshUser.objects.filter(username_id=user.id).first()
            if auth == 'pwd' and password:
                data = {'username_id':user.id,'password':password,'is_key':False}
            elif pkey:
                ssh_key = pkey.read().decode('utf-8')
                data = {'username_id':user.id,'password':password,'ssh_key':ssh_key}
            else:
                return HttpResponse(json.dumps({'status':False,'message':'密码或秘钥文件不能为空'}))
            if not sshuser:
                SshUser.objects.create(**data)
                message = '{} 认证信息保存成功'.format(username)
                status = True
            else:
                message = '{} 认证信息已存在'.format(username)
                status = False
        else:
            status = False
            message = '用户名【{}】不存在，请联系管理员'.format(username)

        return HttpResponse(json.dumps({'status':status,'message':message}))


@login_required
def ssh_terminal(request, pk):
    server_obj = Asset.objects.get(pk=pk)
    ssh_server_ip = server_obj.server.i_ip
    group_name = server_obj.business_unit.name
    username = request.user.username


    if request.method == 'GET':
        download_file = request.GET.get('download_file')

        if download_file:
            download_file_path = os.path.join(settings.MEDIA_ROOT, 'admin_files', username, 'download',
                                              ssh_server_ip)
            sftp = SFTP(ssh_server_ip, request.user.id)
            response = sftp.download_file(download_file, download_file_path)
            return response
        else:
            remote_ip = request.META.get('REMOTE_ADDR')
            return render(request, 'terminal.html', locals())
    elif request.method == 'POST':
        try:
            upload_file = request.FILES.get('upload_file')
            upload_file_path = os.path.join(settings.MEDIA_ROOT, 'fort_files', username, 'upload',
                                            ssh_server_ip)
            # sftp = SFTP(ssh_server_ip, server_obj.port, server_obj.username,
            #             CryptPwd().decrypt_pwd(server_obj.password))
            sftp = SFTP(ssh_server_ip, request.user.id)
            status,message = sftp.upload_file(upload_file, upload_file_path)

            if status:
                code = 200
            else:
                code = 500
            return JsonResponse({'code': code, 'msg': message})
        except Exception as e:
            return JsonResponse({'code': 500, 'msg': '上传失败！{}'.format(e)})


@login_required
def login_fort_record(request):
    if request.method == 'GET':
        user = request.user
        if user.is_superuser:
            results = FortRecord.objects.select_related('login_user').all()
        else:
            results = FortRecord.objects.select_related('login_user').filter(id=user.id)
        return render(request, 'login_admin_record.html', locals())
    elif request.method == 'POST':
        start_time = request.POST.get('startTime')
        end_time = request.POST.get('endTime')
        new_end_time = datetime.datetime.strptime(end_time, '%Y-%m-%d') + datetime.timedelta(1)
        end_time = new_end_time.strftime('%Y-%m-%d')
        try:
            records = []
            search_records = FortRecord.objects.select_related('login_user').filter(start_time__gt=start_time,
                                                                                    start_time__lt=end_time)
            for search_record in search_records:
                record = {
                    'id': search_record.id,
                    'login_user': search_record.login_user.username,
                    'fort': search_record.fort,
                    'record_mode': search_record.get_record_mode_display(),
                    'remote_ip': search_record.remote_ip,
                    'start_time': search_record.start_time,
                    'login_status_time': search_record.login_status_time
                }
                records.append(record)
            return JsonResponse({'code': 200, 'records': records})
        except Exception as e:
            return JsonResponse({'code': 500, 'error': '查询失败：{}'.format(e)})


@login_required
def record_play(request, pk):
    record = FortRecord.objects.select_related('login_user').get(id=pk)
    MEDIA_URL = settings.MEDIA_URL
    if record.record_mode == 'ssh':
        return render(request, 'ssh_record_play.html', locals())
    else:
        return render(request, 'guacamole_record_play.html', locals())