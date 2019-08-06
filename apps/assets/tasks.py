# -*- coding: utf-8 -*-
# @Time    : 2019-07-18 15:04
# @Author  : kbsonlong
# @Email   : kbsonlong@gmail.com
# @Blog    : www.alongparty.cn
# @File    : tasks.py
# @Software: PyCharm


from __future__ import absolute_import,unicode_literals

from django.conf import settings
from celery.utils.log import get_task_logger
from celery import Task
import json

from IDOWN.celery import app

from assets.models import Asset
from .utils.init_system import Init

logger = get_task_logger(__name__)

init = Init()

class demotask(Task):

    def on_success(self, retval, task_id, *args, **kwargs):   # 任务成功执行
        logger.info('task id:{} , arg:{} , successful !'.format(task_id,args))



    def on_failure(self, exc, task_id, args, kwargs, einfo):  #任务失败执行
        logger.info('task id:{} , arg:{} , failed ! erros : {}' .format(task_id,args,exc))


    def on_retry(self, exc, task_id, args, kwargs, einfo):    #任务重试执行
        logger.info('task id:{} , arg:{} , retry !  einfo: {}'.format(task_id, args, exc))




@app.task(base=demotask)
def install_salt_minion():
    """
    安装salt-minion客户端任务
    :param host:   平台地址
    :param server_ip:  待初始化主机
    :return:
    """
    info = {}

    ##cmdb获取到待初始化服务器
    assets = Asset.objects.filter(status=5)
    for asset in assets:
        print(asset.server.i_ip)
        server_ip = asset.server.i_ip
        install_salt_minion = init._install_salt_minion(server_ip)
        init_server = init._init_system(server_ip)
        info.update({server_ip:install_salt_minion,'init_{}'.format(server_ip):init_server})
    assets.update(status=1)
    return info


@app.task
def rsync_config(ips,appname:str,server_host,confname=None)->str:
    """
    同步配置到服务端
    :param ips:  目标主机，多个地址以英文逗号,分隔
    :param appname: 应用名称
    :param server_host: 配置文件下载主机
    :param confname:  配置文件
    :return:
    """
    if confname:
        config_src_path = '{}/{}'.format(settings.MEDIA_URL, confname)
        config_dest_path = '/data/ci/docker/{}/{}'.format(appname, confname)
    else:
        config_src_path = '{}/{}.yml'.format(settings.MEDIA_URL, appname)
        config_dest_path = '/data/ci/docker/{}/{}.yml'.format(appname, appname)
    file_url = '{}/{}'.format(server_host.strip('/'), config_src_path.strip('/'))
    salt_files = init.api.SaltCmd(
        tgt=ips, fun='cp.get_url', client='local',
        tgt_type='list', arg=[file_url, config_dest_path]
    )
    return salt_files

