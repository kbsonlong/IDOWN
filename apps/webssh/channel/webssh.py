# -*- coding: utf-8 -*-
import paramiko
import threading
import time
import os,json
import base64
from socket import timeout

##第三方模块
from channels.generic.websocket import WebsocketConsumer
from django.conf import settings
from django.http.request import QueryDict
from django.utils.six import StringIO
from django.contrib.auth import get_user_model

##自定义模块
from assets.models import Asset
from webssh.models import SshUser,FortRecord
from .tools import get_key_obj
from webssh.tasks import admin_file

User = get_user_model()

class MyThread(threading.Thread):
    def __init__(self, chan):
        super(MyThread, self).__init__()
        self.chan = chan
        self._stop_event = threading.Event()
        self.start_time = time.time()
        self.current_time = time.strftime(settings.TIME_FORMAT)
        self.stdout = []
        self.read_lock = threading.RLock()

    def stop(self):
        self._stop_event.set()

    def run(self):
        with self.read_lock:
            while not self._stop_event.is_set():
                time.sleep(0.1)
                try:
                    data = self.chan.chan.recv(1024)
                    if data:
                        str_data = bytes.decode(data)
                        self.chan.send(str_data)
                        self.stdout.append([time.time() - self.start_time, 'o', str_data])
                except timeout:
                    break
            self.chan.send('\n由于长时间没有操作，连接已断开!')
            self.stdout.append([time.time() - self.start_time, 'o', '\n由于长时间没有操作，连接已断开!'])
            self.chan.close()

    def record(self):
        record_path = os.path.join(settings.MEDIA_ROOT, 'admin_ssh_records', self.chan.scope['user'].username,
                                   time.strftime('%Y-%m-%d'))
        if not os.path.exists(record_path):
            os.makedirs(record_path, exist_ok=True)
        record_file_name = '{}_{}.cast'.format(self.chan.remote_ip, time.strftime('%Y%m%d%H%M%S'))
        record_file_path = os.path.join(record_path, record_file_name)

        header = {
            "version": 2,
            "width": self.chan.width,
            "height": self.chan.height,
            "timestamp": round(self.start_time),
            "title": "Demo",
            "env": {
                "TERM": os.environ.get('TERM'),
                "SHELL": os.environ.get('SHELL', '/bin/bash')
            },
        }

        ##记录操作过程，用于播放webssh录像的插件回放
        # try:
        #     admin_file.delay(record_file_path, self.stdout, header)
        # except:
        admin_file(record_file_path, self.stdout, header)
        # admin_file.apply_async(record_file_path, self.stdout, header)

        login_status_time = time.time() - self.start_time
        if login_status_time >= 60:
            login_status_time = '{} m'.format(round(login_status_time / 60, 2))
        elif login_status_time >= 3600:
            login_status_time = '{} h'.format(round(login_status_time / 3660, 2))
        else:
            login_status_time = '{} s'.format(round(login_status_time))

        print(self.chan.scope['user'])
        try:
            FortRecord.objects.create(
                login_user = self.chan.scope['user'],
                remote_ip = self.chan.ssh_server_ip,
                fort = self.chan.ssh_server_ip,
                start_time = self.current_time,
                login_status_time = login_status_time,
                record_file = record_file_path.split('media/')[1],
                record_mode = 'ssh'
            )
        except Exception as e:
            print('数据库添加用户操作记录失败，原因：{}'.format(e))


class SSHConsumer(WebsocketConsumer):
    def __init__(self, *args, **kwargs):
        super(SSHConsumer, self).__init__(*args, **kwargs)
        self.ssh = paramiko.SSHClient()
        self.group_name = self.scope['url_route']['kwargs']['group_name']

        self.t1 = MyThread(self)
        self.query_string = self.scope.get('query_string')
        self.ssh_args = QueryDict(query_string=self.query_string, encoding='utf-8')
        self.ssh_server_ip = self.ssh_args.get('ssh_server_ip')
        self.remote_ip = self.ssh_args.get('remote_ip')
        self.user = self.ssh_args.get('user')
        self.width = int(self.ssh_args.get('width'))
        self.height = int(self.ssh_args.get('height'))
        self.chan = None

    def connect(self):
        self.accept()
        print(self.user)
        # user = SshUser.objects.get(username =self.user)
        user = User.objects.filter(username=self.user).first()
        # print(user)
        sshuser = SshUser.objects.filter(username_id=user.id).first()
        # print(sshuser)

        try:
            self.ssh.load_system_host_keys()
            self.ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())

            if sshuser.is_key:
                string_io = StringIO()
                string_io.write(sshuser.ssh_key)
                string_io.flush()
                string_io.seek(0)
                ssh_key = string_io
                passwd = sshuser.password

                if passwd:
                    password = base64.b64decode(passwd).decode('utf-8')
                else:
                    password = None
                key = get_key_obj(paramiko.RSAKey, pkey_obj=ssh_key, password=password) or \
                      get_key_obj(paramiko.DSSKey, pkey_obj=ssh_key, password=password) or \
                      get_key_obj(paramiko.ECDSAKey, pkey_obj=ssh_key, password=password) or \
                      get_key_obj(paramiko.Ed25519Key, pkey_obj=ssh_key, password=password)
                self.ssh.connect(username=user.username, hostname=self.ssh_server_ip, port=22, pkey=key,timeout=5)
            else:
                self.ssh.connect(username=user.username, hostname=self.ssh_server_ip, port=22, password=user.password,timeout=5)

            transport = self.ssh.get_transport()
            self.chan = transport.open_session()
            self.chan.get_pty(term='xterm', width=1400, height=self.height)
            self.chan.invoke_shell()
            # 设置如果3分钟没有任何输入，就断开连接
            self.chan.settimeout(60 * 3)
        except Exception as e:
            print('用户{}通过webssh连接{}失败！原因：{}'.format(user.username, self.ssh_server_ip, e))
            self.send('用户{}通过webssh连接{}失败！原因：{}'.format(user.username, self.ssh_server_ip, e))
            self.close()


        self.t1.setDaemon(True)
        self.t1.start()

    def receive(self, text_data=None, bytes_data=None):
        self.chan.send(text_data)

    def disconnect(self, close_code):
        try:
            self.t1.record()
        finally:
            self.ssh.close()
            self.t1.stop()
