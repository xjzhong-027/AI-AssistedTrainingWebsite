from email.policy import default

from django.db import models
import uuid
import os

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
    last_active_time = models.CharField(max_length=50)
    device_info = models.CharField(max_length=500)

class MediaMaterial(models.Model):
    title = models.TextField(default='')
    theme = models.CharField(max_length=50,default='')
    abstract = models.TextField(default='')
    keywords = models.TextField(default='')
    transcript = models.TextField(default='')
    media_url = models.CharField(max_length=100)
    image_url = models.CharField(max_length=100, default='')

class BigQuestion(models.Model):
    media_material = models.ForeignKey(MediaMaterial, on_delete=models.CASCADE, related_name='big_questions')
    # title = models.CharField(max_length=255, verbose_name="大题标题")
    # description = models.TextField(blank=True, verbose_name="大题描述")
    type = models.CharField(verbose_name="题目类型", default="test", max_length=50)
    question_text = models.TextField(verbose_name="大题题干")  # 存储题干
    maximum_play = models.IntegerField(default=3)
    minimum_play = models.IntegerField(default=0)
    start_time = models.DateTimeField(blank=True, null=True)
    end_time = models.DateTimeField(blank=True, null=True)
    created_at = models.DateTimeField(blank=True, auto_now_add=True, verbose_name="创建时间")

    def __str__(self):
        return self.question_text

# 动态生成文件名并设置上传路径。
def upload_to(instance, filename):
    extension = os.path.splitext(filename)[1]  # 获取文件扩展名
    new_filename = f"{uuid.uuid4()}{extension}"  # 生成唯一文件名
    # print(extension)
    # print(f'images/{new_filename}')
    return f"images/{new_filename}"  # 存储到 media/images/

class SmallQuestion(models.Model):
    big_question = models.ForeignKey(BigQuestion, on_delete=models.CASCADE, related_name='small_questions', verbose_name="所属大题")
    question_text = models.TextField(verbose_name='小题内容')
    image_url = models.ImageField(verbose_name="图片", upload_to=upload_to, blank=True, null=True )
    tips = models.TextField(verbose_name='提示', blank=True, null=True)
    answer = models.TextField(verbose_name='参考答案', default='test')
    analysis = models.TextField(verbose_name='解析', blank=True, null=True)
    score = models.FloatField(verbose_name='分数', default=1.0)
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="创建时间")

    def __str__(self):
        return f"{self.big_question} - {self.question_text[:20]}"

# class SmallQuestion(models.Model):
#     big_question = models.ForeignKey(BigQuestion, on_delete=models.CASCADE, related_name='small_questions', verbose_name="所属大题")
#     question_text = models.TextField(verbose_name="小题内容")
#     answer = models.TextField(blank=True, verbose_name="答案")
#     created_at = models.DateTimeField(auto_now_add=True, verbose_name="创建时间")
#
#     def __str__(self):
#         return f"{self.big_question.title} - {self.question_text[:20]}"


# class TemMediaMaterial(models.Model):
#     title = models.TextField(default='')
#     theme = models.CharField(max_length=50,default='')
#     abstract = models.TextField(default='')
#     keywords = models.TextField(default='')
#     transcript = models.TextField(default='')
#     media_url = models.CharField(max_length=100)
#     image_url = models.CharField(max_length=100, default='')

# class TemMainQuestion(models.Model):
#     tem_media_id = models.ForeignKey(TemMediaMaterial, on_delete=models.CASCADE)
#     question = models.TextField(default='')
#     maximum_play = models.IntegerField(default=3)
#     minimum_play = models.IntegerField(default=0)
#     start_time = models.TextField(default='')
#     end_time = models.TextField(default='')

# class TemSubQuestion(models.Model):
#     tem_mainqst_id = models.ForeignKey(TemMainQuestion, on_delete=models.CASCADE,)
#     question = models.TextField()
#     image_url = models.CharField(max_length=100, default='')
#     tips = models.TextField(default='')
#     answers = models.TextField(default='0')
#     analysis = models.TextField(default='')
#     score = models.FloatField(default=1.0)





