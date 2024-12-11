from django.db import models

# Create your models here.

class Students(models.Model):
    username = models.CharField(max_length=20)
    name = models.CharField(max_length=20)
    password = models.CharField(max_length=100)

# Students.objects.create(username='student', name='student1', password='student')
class Teachers(models.Model):
     username = models.CharField(max_length=20)
     name = models.CharField(max_length=20)
     password = models.CharField(max_length=100)
# Teachers.objects.create(username='teacher', name='teacher1', password='teacher')

class Admins(models.Model):
    username = models.CharField(max_length=20)
    password = models.CharField(max_length=100)

# 用户登录记录（ID，学号，周次，行为，时间，最后活动时间，登录设备信息）
class LoginInfo(models.Model):
    username = models.CharField(max_length=20)
    week = models.IntegerField(default=0)
    action = models.CharField(max_length=10)
    action_time = models.DateTimeField()
    last_action_time = models.DateTimeField()
    device_info = models.CharField(max_length=20)


