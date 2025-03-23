from django.db.models.signals import post_save, post_delete

from English_Listening_Website.middleware import SessionTimeoutMiddleware
# from Account.models import Students, Teachers
from .models import LogEntry
from ELW.models import Unit, MediaMaterial
from announce.models import Announcement
from .middleware import get_current_user



def log_create_or_update(sender, instance, created, **kwargs):
    """
    监测教师端的对象创建或更新，记录日志
    """
    if isinstance(instance, sender):
        log_type = 'CREATE' if created else 'UPDATE'
        action = 'Created' if created else 'Updated'
        user = get_current_user()  # 获取当前登录用户
        if not user:
            raise SessionTimeoutMiddleware

        message = f"{action} {str(instance)}"

        # 使用模型的 verbose_name_plural 作为模块名
        module = instance._meta.verbose_name_plural

        # 记录日志到 LogEntry 表
        LogEntry.objects.create(
            user=user,
            log_type=log_type,
            message=message,
            module=module
        )


def log_delete(sender, instance, **kwargs):
    """
    监测教师端的对象删除，记录日志
    """
    if isinstance(instance, sender):
        user = get_current_user()  # 获取当前登录用户
        if not user:
            raise SessionTimeoutMiddleware
        message = f"Deleted {str(instance)}"


        # 使用模型的 verbose_name_plural 作为模块名
        module = instance._meta.verbose_name_plural

        # 记录日志到 LogEntry 表
        LogEntry.objects.create(
            user=user,
            log_type='DELETE',
            message=message,
            module=module
        )

# 使用信号注册器来动态连接信号
def register_signals():
    # 把操作到的表放进来
    post_save.connect(log_create_or_update, sender=Unit)
    post_delete.connect(log_delete, sender=Unit)
    post_save.connect(log_create_or_update, sender=MediaMaterial)
    post_delete.connect(log_delete, sender=MediaMaterial)
    post_save.connect(log_create_or_update, sender=Announcement)
    post_delete.connect(log_delete, sender=Announcement)