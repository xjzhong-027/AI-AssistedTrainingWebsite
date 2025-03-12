from django.db import models
from django.contrib.auth.models import User, Group
from Account.models import Admins


class BackupDatabase(models.Model):
    """ 备份数据库 """
    OPERATIONS = [
        ('backup', 'Backup'),
        ('restore', 'Restore'),
    ]
    STATUS_CHOICES = [
        ('completed', 'Completed'),
        ('failed', 'Failed'),
    ]
    created_at = models.DateTimeField(auto_now_add=True)
    operation = models.CharField(max_length=10, choices=OPERATIONS)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES)
    backup_to = models.CharField(max_length=100)

    class Meta:
        verbose_name_plural = '数据库备份'

    def __str__(self):
        return f"Backup {self.id} - {self.status}"


