from django.db import models
from django.contrib.auth.models import User


class LogEntry(models.Model):
    LOG_TYPE_CHOICES = [
        ('CREATE', 'Create'),
        ('UPDATE', 'Update'),
        ('DELETE', 'Delete'),
    ]

    LOG_STATUS_CHOICES = [
        ('unread', 'Unread'),
        ('read', 'Read'),
    ]

    user = models.ForeignKey(User, null=True, blank=True, on_delete=models.SET_NULL, related_name='log_entries')
    log_type = models.CharField(max_length=20, choices=LOG_TYPE_CHOICES, default='UPDATE')
    message = models.TextField()
    operation_time = models.DateTimeField(auto_now_add=True)
    status = models.CharField(max_length=20, choices=LOG_STATUS_CHOICES, default='unread')
    module = models.CharField(max_length=100, blank=True, null=True)

    class Meta:
        verbose_name_plural = '操作日志'

    def __str__(self):
        return f"[{self.operation_time}] {self.get_log_type_display()} - {self.message[:50]}"

