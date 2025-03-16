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
    if created and instance.is_superuser:  # 检查是否为新创建的超级管理员
        Admins.objects.create(
            username=instance.username,
            password=instance.password,
            user=instance
        )
        print(f"Custom user data added for {instance.username}")