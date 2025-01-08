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

# 动态生成文件名并设置上传路径。
def upload_to(instance, filename):
    extension = os.path.splitext(filename)[1]  # 获取文件扩展名
    new_filename = f"{uuid.uuid4()}{extension}"  # 生成唯一文件名
    # print(extension)
    # print(f'images/{new_filename}')
    return f"images/{new_filename}"  # 存储到 media/images/

# 媒体素材表
class MediaMaterial(models.Model):
    title = models.TextField(default='')
    theme = models.CharField(max_length=50,default='')
    abstract = models.TextField(default='')
    keywords = models.TextField(default='')
    transcript = models.TextField(default='')
    media_url = models.CharField(max_length=100)
    image_url = models.CharField(max_length=100, default='')

# 大题表
class MainQuestion(models.Model):
    QUESTION_TYPES = [
        ('choice', '选择题'),
        ('matching', '连线题'),
        ('correction', '改错题'),
    ]
    media_material = models.ForeignKey(MediaMaterial, on_delete=models.CASCADE, related_name='main_questions')
    question_type = models.CharField(max_length=20, choices=QUESTION_TYPES, default='choice', verbose_name="题目类型")
    question_text = models.TextField(verbose_name="大题题干", blank=False)  # 存储题干
    maximum_play = models.IntegerField(default=3)
    minimum_play = models.IntegerField(default=0)
    start_time = models.DateTimeField(blank=True, null=True)
    end_time = models.DateTimeField(blank=True, null=True)
    created_at = models.DateTimeField(blank=True, auto_now_add=True, verbose_name="创建时间")

    def __str__(self):
        return self.question_text


# 小题表
class SubQuestion(models.Model):
    main_question = models.ForeignKey(MainQuestion, on_delete=models.CASCADE, related_name='sub_questions')
    question_text = models.TextField(verbose_name='小题内容', blank=False, null=False)
    image_url = models.ImageField(verbose_name="图片", upload_to=upload_to, blank=True, null=True )
    tips = models.TextField(verbose_name='提示', blank=True, null=True)
    answer = models.TextField(verbose_name='参考答案', default='test', blank=False)
    analysis = models.TextField(verbose_name='解析', blank=True, null=True)
    score = models.FloatField(verbose_name='分数', default=1.0)
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="创建时间")
    #
    def __str__(self):
        return f"{self.main_question} - {self.question_text[:20]}"

# 选择题-选项表
class ChoiceOption(models.Model):
    sub_question = models.ForeignKey(SubQuestion, on_delete=models.CASCADE, related_name='options')
    option_label = models.CharField(max_length=1, verbose_name="选项字母")
    option_content = models.TextField(verbose_name="选项内容")
    is_answer = models.BooleanField(default=False, verbose_name="是否为答案")

    def __str__(self):
        return f"{self.option_label}: {self.option_content[:20]}"

# 选择题-右项表
class MatchingOption(models.Model):
    sub_question = models.ForeignKey(SubQuestion, on_delete=models.CASCADE, related_name='matchingOptions')
    option_label = models.CharField(max_length=1, verbose_name='选项字母', blank=False, null=False)
    option_content = models.TextField(verbose_name='选项内容')
    image_url = models.ImageField(verbose_name='选项图片', upload_to=upload_to, blank=True, null=True )

    def __str__(self):
        return f"{self.option_label}: {self.option_content[:20]}"


class Correction(models.Model):
    CORRECTION_TYPES = [
        ('insert', '插入'),
        ('delete', '删除'),
        ('revise', '修改')
    ]

    sub_question = models.ForeignKey(SubQuestion, on_delete=models.CASCADE, related_name='correction')
    type = models.CharField(max_length=10, choices=CORRECTION_TYPES, default='insert', verbose_name='改错类型')
    index = models.IntegerField(default=0, verbose_name='修改位置')

    def __str__(self):
        return f"{self.type}"





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





