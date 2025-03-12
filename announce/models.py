from django.db import models
from Account.models import Students, Teachers
from forum.models import Post
# Create your models here.

class Announcement(models.Model):
    """ 公告表 """
    a_title = models.CharField(verbose_name='公告标题', max_length=64)
    a_content = models.CharField(verbose_name='公告内容', max_length=3000, null=True)
    created_at = models.DateTimeField(verbose_name='发布日期', auto_now_add=True)
    receivers = models.ManyToManyField(Students, blank=True, related_name='announcements')
    teachers = models.ForeignKey(Teachers, on_delete=models.CASCADE, related_name='announcements', null=True)

    class Meta:
        verbose_name_plural = '公告管理'

    def __str__(self):
        return f"公告[{self.a_title}] : {self.a_content}"



class Message(models.Model):
    # sender = models.ForeignKey(User, on_delete=models.CASCADE, related_name='sent_messages')
    # receiver = models.ForeignKey(User, on_delete=models.CASCADE, related_name='received_messages')
    sender = models.CharField(max_length=100)  # 发送者用户名
    receiver = models.CharField(max_length=100)  # 接收者用户名
    content = models.TextField()
    is_read = models.BooleanField(default=False)
    read_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    post = models.ForeignKey(Post, on_delete=models.CASCADE, null=True, blank=True, default=None,
                             related_name='messages')
    announcement = models.ForeignKey(Announcement, on_delete=models.CASCADE, null=True, blank=True, default=None,
                                     related_name='messages')
    is_announcement = models.BooleanField(default=False)

    def __str__(self):
        return f"Message from {self.sender} to {self.receiver}"







