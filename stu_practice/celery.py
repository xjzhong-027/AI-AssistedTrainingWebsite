# myproject/celery.py
from __future__ import absolute_import, unicode_literals
import os
from celery import Celery

# 设置默认的 Django 设置模块
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'myproject.settings')

# 创建 Celery 应用
app = Celery('stu_practice')

# 使用 Django 的设置文件配置 Celery
app.config_from_object('django.conf:settings', namespace='CELERY')

# 自动发现并加载任务
app.autodiscover_tasks()