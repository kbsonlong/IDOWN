# -*- coding: utf-8 -*-
# @Time    : 2019-04-30 12:00
# @Author  : kbsonlong
# @Email   : kbsonlong@gmail.com
# @Blog    : www.alongparty.cn
# @File    : saltapi.py
# @Software: PyCharm

import requests
import json

import logging
import urllib3

urllib3.disable_warnings()
logging.captureWarnings(True)



class SaltAPI:
    def __init__(self,url,username,password):
        """

        :param url: http接口地址
        :param username: 认证用户名
        :param password: 认证密码
        """
        self.__url = url.rstrip('/')
        self.__username = username
        self.__password = password
        self.__token_id = self.token_id()
        self.headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/50.0.2661.102 Safari/537.36",
            "Content-type": "application/json"
            # "Content-type": "application/x-yaml"
        }

    # 登陆获取token
    def token_id(self):
        """

        :return: 返回token字符串
        """
        try:
            params = {'eauth': 'pam', 'username': self.__username, 'password': self.__password}
            headers = {'X-Auth-Token': ''}
            url = self.__url + '/login'
            req = requests.post(url=url,headers=headers,data=params,verify=False)
            content = req.json()

            token = content['return'][0]['token']
            return token
        except KeyError:
            raise KeyError

    #推送请求
    def PostRequest(self, obj, prefix='/'):
        """

        :param obj: dict类型数据
        :param prefix:
        :return:
        """
        url = self.__url + prefix
        headers = {'X-Auth-Token': self.__token_id}

        if obj:
            data=obj
            req = requests.post(url=url, data=data, headers=headers, verify=False)
        else:
            req = requests.get(url=url, headers=headers, verify=False)
        content = req.json()
        return content
    #执行命令
    def SaltCmd(self,tgt,fun,client='local',tgt_type='glob',arg=None,**kwargs):
        """

        :param tgt: 标签
        :param fun: 执行函数cmd.run,state.sls等
        :param client: 本地执行local或者后台异步执行localasync
        :param tgt_type: 标签的数据类型,默认glob,list等
        :param arg: 执行函数的参数
        :param kwargs:
        :return:
        """
        params = {'client':client, 'fun':fun, 'tgt':tgt, 'tgt_type':tgt_type}
        if arg:
            params['arg']=arg
        if kwargs:
            print(kwargs)
            params=dict(list(params.items())+list(kwargs.items()))
            print(params)
        res = self.PostRequest(params)
        return res

    #获取JOB ID的详细执行结果
    def SaltJob(self,jid=''):
        """

        :param jid:
        :return:
        """
        if jid:
            prefix = '/jobs/'+jid
        else:
            prefix = '/jobs'
        res = self.PostRequest(None,prefix)

        return res
    #获取grains
    def SaltMinions(self,minion=''):
        """

        :param minion:
        :return:
        """
        if minion and minion!='*':
            prefix = '/minions/'+minion
        else:
            prefix = '/minions'
        res = self.PostRequest(None,prefix)
        return res
    #获取events
    def SaltEvents(self):
        prefix = '/events'
        res = self.PostRequest(None,prefix)
        return res

    def SaltRun(self,tgt,client,fun,tgt_type='glob',arg=None):
        prefix = '/run'
        params = {'client': client, 'fun': fun, 'tgt': tgt, 'tgt_type': tgt_type,'arg':arg}
        res = self.PostRequest(params,prefix)
        return res

    ## wheel
    def SaltWheel(self,tgt,fun,tgt_type='local',client='wheel'):
        params = {'client': client, 'fun': fun, 'tgt': tgt, 'tgt_type': tgt_type }
        res = self.PostRequest(params)
        return res


    #列出KEY
    def ListKey(self):
        prefix = '/keys'
        content = self.PostRequest(None,prefix)
        accepted = content['return']['minions']
        denied = content['return']['minions_denied']
        unaccept = content['return']['minions_pre']
        rejected = content['return']['minions_rejected']
        data={'accepted':accepted,'denied':denied,'unaccept':unaccept,'rejected':rejected}
        return data
    #接受KEY
    def AcceptKey(self, key_id):
        """

        :param key_id: 客户端ID
        :return:
        """
        params = {'client': 'wheel', 'fun': 'key.accept', 'match': key_id}
        content = self.PostRequest(params)
        ret = content['return'][0]['data']['success']
        return ret
    # #删除KEY
    def DeleteKey(self, key_id):
        """

        :param key_id: 客户端ID
        :return:
        """
        params = {'client': 'wheel', 'fun': 'key.delete', 'match': key_id}
        content = self.PostRequest(params)
        ret = content['return'][0]['data']['success']
        return ret



#测试：python manager.py shell ; from SALT.SaltAPI import * ; main()，代码修改了要ctrl+Z退出重进
def main():
    sapi = SaltAPI(url="https://192.168.16.102:8200",username="salt",password="salt")
    # job = sapi.SaltCmd('192.168.16.102','cmd.run',client='local',arg='salt-ssh  -i 192.168.16.102 test.ping' ,tgt_type='glob',timeout=20)
    job = sapi.SaltJob('20190613184853323015')
    print(job)
    # print(job)
    # job_id = job['return'][0]['jid']
    # print(sapi.look_jid(job_id))
    # print(sapi.SaltJob('20190510043632206140'))-
    # print(job)
    print(sapi.token_id())
    # roots = sapi.SaltWheel(tgt='192.168.56.101', client='wheel', fun='file_roots.list_roots')
    # print(roots)
    # print(sapi.SaltRun(tgt='192.168.16.102',client='local',fun='cmd.run',arg=' -i free -m '))
    # print(sapi.SaltCmd(tgt='192.168.16.102',fun='state.sls',client='local',arg='base.init',arg1='saltenv=base'))
    # print(sapi.SaltWheel('192.168.56.101',fun='file_roots.list_roots')['return'][0]['data']['return'])
    # print(sapi.SaltCmd(client='local', tgt= '192.168.56.101', fun='state.sls', arg= 'user_manage.fangjiayu'))
    # salt_usermode= sapi.SaltCmd(
    #     tgt='baibu', fun='cp.get_url',client='local',
    #     tgt_type='nodegroup',arg=['http://192.168.56.1:8000/media/user/liugenbao.sls','/data/salt/base/user_manage/liugenbao.sls']
    # )
    # print(salt_usermode)
    # print(sapi.SaltCmd(client='local', tgt= '192.168.56.101', fun='cp.get_url', arg= ['http://192.168.56.1:8000/media/user/zengshenglong.sls','/tmp/test.sls']))
if __name__ == '__main__':
    main()