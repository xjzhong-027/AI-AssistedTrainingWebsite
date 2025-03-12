from django.db.models.signals import post_delete
from django.dispatch import receiver
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