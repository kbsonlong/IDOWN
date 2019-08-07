from django.test import TestCase

# Create your tests here.

import os
import logging
import paramiko
import base64
from io import StringIO


def get_key_obj(pkeyobj, pkey_file=None, pkey_obj=None, password=None):
    """
    解密私钥
    :param pkeyobj:
    :param pkey_file:
    :param pkey_obj:
    :param password:
    :return:
    """
    if pkey_file:
        with open(pkey_file) as fo:
            try:
                pkey = pkeyobj.from_private_key(fo, password=password)
                return pkey
            except:
                pass
    else:
        try:
            pkey = pkeyobj.from_private_key(pkey_obj, password=password)
            return pkey
        except:
            pkey_obj.seek(0)


class SFTP:
    def __init__(self, host, username, password=None, key_file=None):
        self.username = username
        self.transport = paramiko.Transport(sock="{}:{}".format(host, 22))

        # passwd = password
        # if passwd:
        #     password = base64.b64decode(passwd).decode('utf-8')
        # else:
        #     password = None

        if key_file:
            with open(key_file, 'r') as f:
                ssh_key = f.read()
            f.close()
            string_io = StringIO()
            string_io.write(ssh_key)
            string_io.flush()
            string_io.seek(0)
            ssh_key = string_io
            key = get_key_obj(paramiko.RSAKey, pkey_obj=ssh_key, password=password) or \
                  get_key_obj(paramiko.DSSKey, pkey_obj=ssh_key, password=password) or \
                  get_key_obj(paramiko.ECDSAKey, pkey_obj=ssh_key, password=password) or \
                  get_key_obj(paramiko.Ed25519Key, pkey_obj=ssh_key, password=password)
            self.transport.connect(username=self.username, pkey=key)
        else:
            self.transport.connect(username=self.username, password=password)

        self.sftp = paramiko.SFTPClient.from_transport(self.transport)


    def put_file(self, local_file, remote_path):
        """
        :param local_file: 本地文件的路径
        :param remote_path: 远程服务器存放目录，路径最后没有"/"
        """
        try:
            filename = local_file.split('/')[-1]
            remote_file = '{}/{}'.format(remote_path, filename)
            self.sftp.put(local_file, remote_file)
            file_stat = self.sftp.stat(remote_file)
        except Exception as e:
            logging.getLogger().error(e)
        finally:
            self.transport.close()


    def get_file(self, remote_file, local_file):
        try:
            self.sftp.get(remote_file, local_file)
        except Exception as e:
            logging.getLogger().error(e)
        finally:
            self.transport.close()


from sqlalchemy import create_engine, Table, MetaData
from sqlalchemy.orm import Session
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import sessionmaker
from sqlalchemy.exc import IntegrityError
# 调用操作链接,反查
from sqlalchemy.orm import relationship


class SqlDB(object):
    def __init__(self,host,username,password,dbname,port=3306):
        self.engine=create_engine("mysql+pymysql://{}:{}@{}:{}/{}".format(username,password,host,port,dbname),encoding='utf-8',echo=True)
        self.metadata = MetaData(self.engine)
        self.session = Session(self.engine)
        self.Base = automap_base()

    def commit(self):
        self.session.commit()

    def rollback(self):
        self.session.rollback()




if __name__ == '__main__':
    sftp = SFTP('seam.alongparty.cn',username='root',password='kbsonlong',key_file='D:\work\id_dsa_1024')

    sftp.put_file('D:\work\Static_Full_Version.zip','/tmp/')


    username='root'
    password='123456'
    dbname='sops_v2'
    host = '192.168.16.102'
    port=3306
    engine = create_engine("mysql+pymysql://{}:{}@{}:{}/{}".format(username, password, host, port, dbname),
                                encoding='utf-8', echo=True)
    metadata = MetaData(engine)
    session = Session(engine)
    Base = automap_base()
    Base.prepare(engine, reflect=True)
    packages = Base.classes.ops_app_packages
    package_version = Base.classes.ops_package_version
    inser_data = {'package_name':'test3','package_path':'/data/images/test/','app_id':1,'env_id':2}
    pre_key = {'app_id':1,'env_id':2,'package_name':'test3'}
    data = session.query(packages).filter_by(**pre_key).first()
    print(data)
    if not data:
        package = session.add(packages(**inser_data))
        data = session.query(packages).filter_by(**inser_data).first()

    version_data = {'package_version': '201707251437', 'package_id': data.id}
    session.add(package_version(**version_data))

    print(data.id)
    # try:
    #     session.merge(packages(**inser_data))
    # except IntegrityError:
    #     session.query(packages).filter_by(**pre_key).first()

    # session.commit()
    # print(package.id)