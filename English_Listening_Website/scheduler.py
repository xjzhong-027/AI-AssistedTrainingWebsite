# scheduler.py
from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.jobstores.memory import MemoryJobStore
from apscheduler.executors.pool import ThreadPoolExecutor, ProcessPoolExecutor
from django.conf import settings
import threading

jobstores = {
    'default': MemoryJobStore()
}
executors = {
    'default': ThreadPoolExecutor(20),
    'processpool': ProcessPoolExecutor(5)
}
job_defaults = {
    'coalesce': False,
    'max_instances': 3
}

scheduler = BackgroundScheduler(jobstores=jobstores, executors=executors, job_defaults=job_defaults)

# 使用一个锁来确保调度器只被启动一次
scheduler_lock = threading.Lock()

def start_scheduler():
    with scheduler_lock:
        if not scheduler.running:
            scheduler.start()

# 在 asgi.py 中调用 start_scheduler 函数