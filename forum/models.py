from django.contrib.auth.models import AbstractUser
from django.db import models
from django.utils import timezone
from django import forms
from ELW.models import MainQuestion,SubQuestion
from Account.models import Students, Teachers


class Post(models.Model):
    title = models.CharField(max_length=200)
    content = models.TextField()
    created_at = models.DateTimeField(default=timezone.now)
    is_top = models.BooleanField(default=False)
    top_score = models.IntegerField(default=0)#精选值
    is_question = models.BooleanField(default=False, verbose_name="是否关于题目")
    is_public = models.BooleanField(default=True)#是否公开，不公开则与老师私聊
    teacher = models.ForeignKey(Teachers, on_delete=models.CASCADE, related_name='posts', null=True, blank=True)
    student = models.ForeignKey(Students, on_delete=models.CASCADE, related_name='posts', null=True, blank=True)
    author =  models.CharField(max_length=100, null=True, blank=True)
    is_anonymous = models.BooleanField(default=False)
    anonymous_name = models.CharField(max_length=100, null=True, blank=True)  # 匿名名称
    name = models.CharField(max_length=100, null=True, blank=True)  # 帖子显示的名字
    is_announcement = models.BooleanField(default=False)  # 是否与公告
    main_question = models.ForeignKey(MainQuestion, on_delete=models.CASCADE, null=True, blank=True,
                                      related_name='posts')
    sub_question = models.ForeignKey(SubQuestion, on_delete=models.CASCADE, null=True, blank=True,
                                      related_name='posts')

    def __str__(self):
        return self.title

    def save(self, *args, **kwargs):
        # 动态设置 name 字段
        if self.anonymous_name:
            self.name = self.anonymous_name
        elif self.teacher:
            self.name = self.teacher.name
        elif self.student:
            self.name = self.student.name
        super().save(*args, **kwargs)



class Comment(models.Model):
    post = models.ForeignKey(Post, on_delete=models.CASCADE, related_name='comments')  # 关联到帖子
    parent_comment = models.ForeignKey('self', on_delete=models.CASCADE, null=True, blank=True,
                                       related_name='replies')  # 父评论
    created_at = models.DateTimeField(default=timezone.now)  # 评论时间
    content = models.TextField()  # 评论内容
    is_top = models.BooleanField(default=False)  # 置顶
    is_marked = models.BooleanField(default=True)  # 其他标记，默认为True
    #author = models.ForeignKey(User, on_delete=models.CASCADE, related_name='comments', null=True)#登陆用户名
    teacher = models.ForeignKey(Teachers, on_delete=models.CASCADE, related_name='comments', null=True, blank=True)
    student = models.ForeignKey(Students, on_delete=models.CASCADE, related_name='comments', null=True, blank=True)
    author = models.CharField(max_length=100, null=True, blank=True)
    is_anonymous = models.BooleanField(default=False)
    name = models.CharField(max_length=100, null=True, blank=True)
    anonymous_name = models.CharField(max_length=100, null=True, blank=True)#匿名

    def save(self, *args, **kwargs):
        # 动态设置 name 字段
        if self.anonymous_name:
            self.name = self.anonymous_name
        elif self.student:
            self.name = self.student.name
        elif self.teacher:
            self.name = self.teacher.name
        super().save(*args, **kwargs)

    def __str__(self):
        return f"Comment on {self.post.title} by {self.name}"


class Anonymous(models.Model):
    user = models.ForeignKey(Students, on_delete=models.CASCADE, related_name='anonymous_names')
    post = models.ForeignKey(Post, on_delete=models.CASCADE, related_name='anonymous_posts')
    anonymous_name = models.CharField(max_length=50)

    class Meta:
        unique_together = (('user', 'post'),)

    def __str__(self):
        return self.anonymous_name






