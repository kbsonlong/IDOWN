# -*- coding: utf-8 -*-
# @Time    : 2019-08-02 10:28
# @File    : fabfile.py
# @Software: PyCharm

import pymysql
from datetime import datetime
from os.path import *

from fabric.api import *

env.user = "root"
env.password = "111111"

##
dbuser='root'
dbpwd='123456'
dbname='ops_manage'
dbhost='192.168.16.102'
dbport=3306

# 各远端项目工作根目录
env.deploy_work_root = '/data/ci/docker/'
# 各远端项目日志根目录
env.deploy_log_root = '/data/logs/'

# 分发机(本机)的包仓库
env.deploy_repository = '/data/devops/repository/'




class Item(object):
    def __init__(self, env_name, service_name, ips, jdk_options):
        self.env_name = env_name
        self.service_name = service_name
        self.ips = ips
        self.jdk_options = jdk_options

    def get_key(self):
        return self.env_name + "@" + self.service_name

    def get_env_name(self):
        return self.env_name

    def get_service_name(self):
        return self.service_name

    def get_ips(self):
        return self.ips

    def get_repository_path(self):
        """
        仓库目录
        :return:
        """
        return join(env.deploy_repository, self.env_name)

    def get_work_path(self):
        """
        工作目录
        :return:
        """
        return join(env.deploy_work_root, self.service_name)

    def get_logs_path(self):
        """
        日志目录
        :return:
        """
        return join(env.deploy_log_root, self.service_name)

    def get_options(self):
        return self.jdk_options

    def get_file_name_length(self):
        return len(self.get_service_name()) + 4 + 11

    def get_clear_shell(self, size: int):
        """
        获取清理Jar包的脚本，用于删除本地仓库，及远端
        :param size: 保留的数量
        :return:
        """
        return "ls -lt {name}-*.?ar |awk '{{if (length($9)=={len}) print $9}}'" \
               "|awk '{{if(NR>{size})print $NF}}'|xargs rm -rf".format(
            name=self.get_service_name(), len=self.get_file_name_length(), size=size)

class Dispatcher(object):
    def __init__(self, items):
        self.m = {}
        for t in items:
            self.m[t.get_key()] = t

    def register(self, t: Item):
        """
        注册
        :param t:
        :return:
        """
        self.m[t.get_key()] = t
        return self

    def get_item(self, env_name, service_name):
        o = self.m.get(env_name + "@" + service_name)
        if not o:
            abort("环境 {0} 未设定服务{1}的工作节点.".format(env_name, service_name))
        return o


# JDK1.8镜像
JDK_IMAGES = 'registry.cn-hangzhou.aliyuncs.com/zhijing/jdk-1.8.0_73_centos:latest'

# # 开发环境Spring启动参数
# DEV_JAVA_OPTIONS = "-Dspring.profiles.active=dev -Xms512m -Xmx512m -Dlogging.path=/data/server/tomcat/logs"
#
#
# item1 = Item("dev", "analysis_server", ["192.168.16.140"], DEV_JAVA_OPTIONS)
# item2 =   Item("dev", "open-api-dubbo-provider", ["192.168.16.140", "192.168.16.141"], DEV_JAVA_OPTIONS)
# item3 =   Item("dev", "open-api-http-provider", ["192.168.16.141"], DEV_JAVA_OPTIONS)
#
# items = [
#     item1,item2,item3
# ]
#
#
# D = Dispatcher(items)




def get_file_extension(fullname):
    if fullname.endswith(".war"):
        return "war"
    return "jar"


##从数据库获取变量
class Readconf(object):

    def __init__(self):
        self.dbuser = dbuser
        self.dbpwd = dbpwd
        self.dbname = dbname
        self.dbhost = dbhost
        self.dbport = dbport
        self.conn = pymysql.connect(user=self.dbuser, password=self.dbpwd, host=self.dbhost, port=self.dbport,
                                    database=self.dbname, charset='utf8')

    def get_option(self,env_name,service_name,commpany="baibu"):
        """

        :param env_name:  环境名
        :param service_name: 服务名称
        :param commpany:
        :return:
        """
        cursor = self.conn.cursor(cursor=pymysql.cursors.DictCursor)
        # cursor = self.conn().cursor()
        sql = """select env,name,i_ip,value,value2 from op_apps_m where env='{}' and name='{}' and company='{}' and active !=9 and service_name='jar'""".format(env_name,service_name,commpany)
        print(sql)
        cursor.execute(sql)
        results = cursor.fetchall()
        rs = []
        ips=[]
        for result in results:
            print(result)
            ips.append(result['i_ip'])
            jvm_options = "{} {}".format(result['value'].strip('"').strip("'").strip("0"),result['value2'].strip('"').strip("'").strip("0"))
            # rs.extend([result['env'],result['name'],result['i_ip'],"{} {}".format(result['value'].strip('"').strip("'").strip("0"),result['value2'].strip('"').strip("'").strip("0"))])
        rs.extend([ips,jvm_options])
        print(rs)
        return rs





@runs_once
def clear_jar(i: Item):
    print("### Clear Local Jar ...")
    with lcd(i.get_repository_path()):
        local(i.get_clear_shell(10))


def get_lasted_jar(i: Item):
    """
    返回文件名，不是路径
    :param i:
    :return:
    """
    with lcd(i.get_repository_path()):
        # 如果存在刚上传的，重命名
        jar_lasted = local("ls -lt {name}.*ar|awk '{{print($9)}}'|head -1".format(name=i.get_service_name()),
                           capture=True)
        if jar_lasted:
            local("mv ./{0} ./{1}-{2}.{3}".format(jar_lasted, i.get_service_name(),
                                                  datetime.now().strftime('%y%m%d%H%M'),
                                                  get_file_extension(jar_lasted)))

        # 1.获取本地的最近Jar
        jar_lasted = local(
            "ls -lt {name}-*.?ar |awk '{{if (length($9)=={len}) print ($9)}}'|head -1".format(name=i.get_service_name(),
                                                                                              len=i.get_file_name_length()),
            capture=True)

        if not jar_lasted:
            abort("分发服务异常，环境{0}找不到 {1} 对应的Jar.".format(i.get_env_name(), i.get_service_name()))
            return
        return jar_lasted


@task()
def deploy(service_name, env_name="dev",):
    """
    部署服务
    :param service_name:  服务名
    :param env_name:  环境名
    :return:
    """

    rc = Readconf()
    ips, jdk_options = rc.get_option(env_name, service_name)
    D = Dispatcher([Item(env_name, service_name, ips, jdk_options)])

    i = D.get_item(env_name, service_name)
    clear_jar(i)
    env.roledefs['ips'] = i.get_ips()

    print(u"###  部署开始  ###")
    execute(do, i)
    print(u"###  部署完成  ###")


@task()
def rollback(service_name, env_name="dev"):
    """
    版本回退
    :param service_name: 服务名
    :param env_name: 环境名
    :return:
    """

    rc = Readconf()
    ips, jdk_options = rc.get_option(env_name, service_name)
    D = Dispatcher([Item(env_name, service_name, ips, jdk_options)])

    i = D.get_item(env_name, service_name)
    # 获取最新文件
    jar_lasted = get_lasted_jar(i)

    # 备份
    with lcd(i.get_repository_path()):
        print(u"### 文件备份  ###")
        local("mv {0} {0}.rollback".format(jar_lasted))

    deploy(service_name, env_name)


@roles('ips')
def do(i: Item):
    """
    部署实现过程
    :param i:
    :return:
    """
    # 1.获取最近Jar
    jar_lasted = get_lasted_jar(i)
    print(jar_lasted)


    # 2.工作目录不存在，则创建
    work_path = i.get_work_path()

    run('if [ ! -d "{0}" ]; then  mkdir -p {0} ;fi '.format(work_path))
    run('if [ ! -d "{0}" ]; then  mkdir -p {0} ;fi && chmod -R 777 {0}'.format(i.get_logs_path()))

    # 3.上传文件id
    put(join(i.get_repository_path(), jar_lasted), work_path)

    # 4.停止并销毁已有实例
    print(u"###  停止并销毁已有实例  ###")

    container_id = run('docker ps -a -q -f"name={0}"'.format(i.get_service_name()))
    # print(container_id)
    if container_id:
        run('docker stop {0} && docker rm {0}'.format(container_id))

    print(u"###  启动新实例  ###")
    # 5.启动新实例
    run(
        'docker run -itd --net=host --cap-add=SYS_PTRACE --log-driver=none --restart=always '
        '--name {NAME} '
        '-v /etc/hosts:/etc/hosts '
        '-v /data/server:/data/server '
        '-v {ROOT}:/work '
        '-v {LOGS}:/data/server/tomcat/logs '
        '-e SW_AGENT_NAME={ENV}-{NAME} '
        '-e SW_AGENT_COLLECTOR_BACKEND_SERVICES={ENV}-skywalking.baibu.la:11800 '
        '-v /data/server/skywalking-agent:/skywalking-agent '
        '{JDK_IMAGES} '
        'java {OPTIONS} -javaagent:/skywalking-agent/skywalking-agent.jar  -jar /work/{JAR_NAME}'.format(ROOT=work_path,
                                                      LOGS=i.get_logs_path(),
                                                      NAME=i.get_service_name(),
                                                      ENV=i.get_env_name(),
                                                      JDK_IMAGES=JDK_IMAGES,
                                                      OPTIONS=i.get_options(),
                                                      JAR_NAME=jar_lasted))
    # 6. 清理原来的Jar
    with cd(work_path):
        run(i.get_clear_shell(1))

# fab -f test_fabric.py start --hide status,running,stdout,user,aborts,warnings,stderr

# fab deploy:service_name,env_name