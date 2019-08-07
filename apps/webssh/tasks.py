# -*- coding: utf-8 -*-
# @Time    : 2019-07-18 13:36
# @Author  : kbsonlong
# @Email   : kbsonlong@gmail.com
# @Blog    : www.alongparty.cn
# @File    : tasks.py
# @Software: PyCharm

import json
import logging
from IDOWN.celery import app

@app.task
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
