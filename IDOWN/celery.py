# -*- coding: utf-8 -*-
# @Time    : 2019-06-18 10:47
# @Author  : kbsonlong
# @Email   : kbsonlong@gmail.com
# @Blog    : www.alongparty.cn
# @File    : main.py
# @Software: PyCharm

from __future__ import absolute_import, unicode_literals

from django.conf import settings
from celery import Celery
import os
from kombu import Queue, Exchange


# 设置celery环境变量
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'Sops.settings.dev')

REDIS_INFO = '{}:{}'.format(settings.REDIS_HOST,settings.REDIS_PORT)
BROKER_URL = 'redis://{}/{}'.format(REDIS_INFO,settings.REDIS_DB)
# celery配置
CELERY_RESULT_SERIALIZER = 'json'
CELERY_TASK_SERIALIZER = 'pickle'
CELERY_ACCEPT_CONTENT = ['pickle', 'json']
CELERYD_MAX_TASKS_PER_CHILD = 40  #  每个worker最多执行40个任务就会被销毁，可防止内存泄露
CELERY_TRACK_STARTED = True


CELERY_RESULT_BACKEND = 'django-db'   ##使用django-orm
DJANGO_CELERY_BEAT_TZ_AWARE = False
CELERY_TIMEZONE='Asia/Shanghai',
CELERY_ENABLE_UTC=False,
CELERY_TASK_RESULT_EXPIRES = 60 * 60 * 24 * 7 # 任务过期时间
CELERY_BEAT_SCHEDULER = 'django_celery_beat.schedulers:DatabaseScheduler'
app = Celery('Sops',
             broker=BROKER_URL,
             backend=CELERY_RESULT_BACKEND,
             )
# Optional configuration, see the application user guide.
app.conf.update(
    task_serializer='json',
    accept_content=['json'],  # Ignore other content
    result_serializer='json',
    timezone='Asia/Shanghai',
    task_default_queue = 'default',
    task_default_exchange = 'default',
    task_default_exchange_type = 'direct',
    task_default_routing_key = 'default',
)

CELERY_ROUTES = {
    'assets.tasks.*': {'queue': 'default', 'routing_key': 'default'},
    'webssh.tasks.*': {'queue': 'default', 'routing_key': 'webssh'},
    'saltapp.tasks.*': {'queue': 'ansible', 'routing_key': 'saltstack'},
    'fort.tasks.*': {'queue': 'fort', 'routing_key': 'fort'},
}

app.conf.task_queues = (
    Queue('default', Exchange('default', type='direct'), routing_key='default'),
    Queue('webssh', Exchange('webssh', type='direct'), routing_key='webssh'),
    Queue('fort', Exchange('fort', type='direct'), routing_key='fort'),
    Queue('plan', Exchange('plan', type='direct'), routing_key='plan'),
)

app.config_from_object('django.conf:settings', namespace='CELERY')
app.autodiscover_tasks()


if __name__ == '__main__':
    app.start()