from django.db.models.signals import post_delete, post_save
from django.dispatch import receiver
from django.contrib.auth.models import User
from .models import Admins, Teachers, Students

# 删除admin, teacher, student时触发信号，同时删除对应在User表里的实例
@receiver(post_delete, sender=Admins)
def delete_associated_user(sender, instance, **kwargs):
    if instance.user:
        instance.user.delete()

@receiver(post_delete, sender=Teachers)
def delete_associated_user(sender, instance, **kwargs):
    if instance.user:
        instance.user.delete()

@receiver(post_delete, sender=Students)
def delete_associated_user(sender, instance, **kwargs):
    if instance.user:
        instance.user.delete()



@receiver(post_save, sender=User)
def create_admins_for_superuser(sender, instance, created, **kwargs):
    # 注意：这里不自动创建 Admins，因为 instance.password 已经是加密后的密码
    # 如果需要创建超级管理员对应的 Admins，请使用 create_custom_superuser 命令
    # 或者通过 Django admin 界面手动创建（此时会使用明文密码）
    pass