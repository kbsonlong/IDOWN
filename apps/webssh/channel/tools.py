#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Author  : HuYuan
# @File    : tools.py

import time
import random
import hashlib
import json

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

def unique():
    ctime = str(time.time())
    salt = str(random.random())
    m = hashlib.md5(bytes(salt, encoding='utf-8'))
    m.update(bytes(ctime, encoding='utf-8'))
    return m.hexdigest()


def admin_file(filename, txts, header=None):
    """
    保存webssh操作过程
    :param filename:
    :param txts:
    :param header:
    :return:
    """
    try:
        if header:
            f = open(filename, 'a')
            f.write(json.dumps(header) + '\n')
            for txt in txts:
                f.write(json.dumps(txt) + '\n')
            f.close()
        else:
            with open(filename, 'a') as f:
                for txt in txts:
                    f.write(txt)
    except Exception as e:
        print('添加用户操作记录文件失败，原因：{}'.format(e))