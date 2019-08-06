# -*- coding: utf-8 -*-
# @Time    : 2019-06-03 18:19
# @Author  : kbsonlong
# @Email   : kbsonlong@gmail.com
# @Blog    : www.alongparty.cn
# @File    : init_system.py
# @Software: PyCharm

import os
from django.conf import settings
from .saltapi import SaltAPI


class Init(object):
    def __init__(self):
        master = settings.SALT_MASTER
        username = settings.SALT_USER
        password = settings.SALT_PASSWD
        port = settings.SALT_API_PORT
        self.api = SaltAPI(url="https://{}:{}".format(master,port),username=username,password=password)
        self.master = master

    def _install_salt_minion(self,server_ip):
        """
        通过salt-ssh安装salt-minion
        :param server_ip:
        :return:
        """
        with open('/{}/salt_state/{}'.format(settings.MEDIA_ROOT.strip('/'), 'roster'), 'r') as t:
            roster = t.read()
        t.close()
        with open('{}/roster'.format(settings.MEDIA_ROOT), 'a') as f:
            files = roster.format(server_ip, server_ip)
            f.write(files)
        f.close()
        new_roster = self.api.SaltCmd(
            tgt=self.master, fun='cp.get_url', client='local',
            tgt_type='glob',
            arg=['{}/media/roster'.format(settings.SERVER_HOST.strip('/')), '/etc/salt/roster']
        )
        info = self.api.SaltCmd(tgt=self.master, fun='cmd.run', client='local_async', arg='salt-ssh  -i {} state.sls base.salt-minion'.format(server_ip),
                           tgt_type='glob', timeout=20,arg1='saltenv=base')
        info.update({'new_roster':new_roster})
        os.remove('/{}/roster'.format(settings.MEDIA_ROOT.strip('/')))
        return info

    def _init_system(self,server_ip):
        """
        初始化服务器
        :param server_ip: 初始化主机地址
        :return: job_id: salt异步任务ID
        """
        job_id = self.api.SaltCmd(tgt=server_ip,fun='state.sls',client='local_async',arg='base.init',arg1='saltenv=base')
        return job_id