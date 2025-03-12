from email.policy import default

from django.db import models
import uuid
import os

from Account.models import Students, Teachers, Class, Course, Admins, Attendance

# Create your models here.

# 教师表
# class Teachers(models.Model):
#     username = models.CharField(max_length=20, verbose_name='账号')
#     name = models.CharField(max_length=20, verbose_name='姓名')
#     password = models.CharField(max_length=100)
# # Teachers.objects.create(username='teacher', name='teacher1', password='teacher')
#
# # 课程表
# class Course(models.Model):
#     year = models.IntegerField(verbose_name='开课年份', blank=False, null=False)
#     grade = models.IntegerField(verbose_name='开课年级', blank=False, null=False,
#                                 choices=[(1, '大一'), (2, '大二'), (3, '大三'), (4, '大四')])
#     semester = models.IntegerField(verbose_name='开课学期', blank=False, null=False,
#                                    choices=[(1, '上学期'), (2, '下学期')])
# # 班级表
# class Class(models.Model):
#     course = models.ForeignKey(Course, on_delete=models.CASCADE, related_name='course')
#     teacher = models.ForeignKey(Teachers, on_delete=models.CASCADE, related_name='teacher_id')
#     start_date = models.CharField(verbose_name='开课日期', blank=True, null=True, max_length=20)
#     week = models.IntegerField(verbose_name='周几上课', blank=False, null=False,
#                                choices=[(1, '周一'), (2, '周二'), (3, '周三'), (4, '周四'), (5, '周五'), (6, '周六'), (7, '周日')])
#     start_time = models.CharField(verbose_name='上课时间', blank=False, null=False, max_length=50)
#     end_time = models.CharField(verbose_name='下课时间', blank=False, null=False, max_length=50)
#
# # 学生表
# class Students(models.Model):
#     class_instance = models.ForeignKey(Class, on_delete=models.CASCADE, related_name='class_id')
#     username = models.CharField(verbose_name='学生账号', max_length=20)
#     name = models.CharField(verbose_name='学生姓名', max_length=20)
#     password = models.CharField(verbose_name='学生密码', max_length=100)
# Students.objects.create(username='student', name='student1', password='student')

# 考勤记录表
# class Attendance(models.Model):
#     student = models.ForeignKey(Students, on_delete=models.CASCADE, related_name='student_id')
#     week = models.IntegerField(verbose_name='周次', blank=False, null=False)
#     status = models.CharField(verbose_name='考勤状况', blank=False, null=False, max_length=20,
#                               choices=[('normal', '正常出勤'), ('absent', '缺勤'), ('late', '迟到'),
#                                        ('early-leave', '早退'), ('abnormal', '异常挂机'), ('late and early-leave', '迟到+早退'),
#                                        ('vacation', '假期')],
#                               default='absent')
#
# # 管理员表
# class Admins(models.Model):
#     username = models.CharField(max_length=20)
#     password = models.CharField(max_length=100)

# 用户登录记录（ID，学号，周次，行为，时间，最后活动时间，登录设备信息）
class LoginInfo(models.Model):
    username = models.CharField(max_length=20)
    week = models.IntegerField(default=0)
    action = models.CharField(max_length=20)
    action_time = models.DateTimeField()
    last_active_time = models.CharField(max_length=50)
    device_info = models.CharField(max_length=500)

# 动态生成文件名并设置上传路径。
def images_upload_to(instance, filename):
    extension = os.path.splitext(filename)[1]  # 获取文件扩展名
    new_filename = f"{uuid.uuid4()}{extension}"  # 生成唯一文件名
    # print(extension)
    # print(f'images/{new_filename}')
    return f"images/{new_filename}"  # 存储到 media/images/

def documents_upload_to(instance, filename):
    extension = os.path.splitext(filename)[1]
    new_filename = f"{uuid.uuid4()}{extension}"
    return f"documents/{new_filename}"

# 媒体素材表
class MediaMaterial(models.Model):
    title = models.TextField(default='')
    theme = models.CharField(max_length=50,default='')
    abstract = models.TextField(default='')
    keywords = models.TextField(default='')
    transcript = models.TextField(default='')
    media_url = models.CharField(max_length=100)
    image_url = models.CharField(max_length=100, default='')

    def __str__(self):
        return self.title

# 大题表
class MainQuestion(models.Model):
    QUESTION_TYPES = [
        ('choice', '选择题'),
        ('matching', '连线题'),
        ('correction', '改错题'),
        ('comprehension', '主观题'),
    ]
    media_material = models.ForeignKey(MediaMaterial, on_delete=models.CASCADE, related_name='main_questions')
    question_type = models.CharField(max_length=20, choices=QUESTION_TYPES, default='choice', verbose_name="题目类型")
    question_text = models.TextField(verbose_name="大题题干", blank=False)  # 存储题干
    maximum_play = models.IntegerField(default=3)
    minimum_play = models.IntegerField(default=0)
    start_time = models.TimeField(blank=True, null=True)
    # mid_time = models.TimeField(blank=True, auto_now_add=True, null=True)
    end_time = models.TimeField(blank=True, null=True)
    allow_pause = models.BooleanField(blank=True, null=True, default=False)
    limited_time = models.TimeField(blank=True, null=True)
    created_at = models.DateTimeField(blank=True, auto_now_add=True, verbose_name="创建时间")

    def __str__(self):
        return self.question_type


# 上传的word文件
class Document(models.Model):
    uploaded_at = models.DateTimeField(auto_now_add=True)
    document_url = models.FileField(verbose_name='文件', upload_to=documents_upload_to, blank=False, null=False)
    content = models.TextField(blank=True)  # 用于存储文档解析后的内容

# 小题表
class SubQuestion(models.Model):
    main_question = models.ForeignKey(MainQuestion, on_delete=models.CASCADE, related_name='sub_questions')
    question_text = models.TextField(verbose_name='小题内容', blank=False, null=False)
    image_url = models.ImageField(verbose_name="图片", upload_to=images_upload_to, blank=True, null=True)
    tips = models.TextField(verbose_name='提示', blank=True, null=True)
    answer = models.TextField(verbose_name='参考答案', default='test', blank=False)
    analysis = models.TextField(verbose_name='解析', blank=True, null=True)
    score = models.FloatField(verbose_name='分数', default=1.0)
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="创建时间")
    #
    def __str__(self):
        return f"main_question-{self.main_question}"

# 选择题-选项表
class ChoiceOption(models.Model):
    sub_question = models.ForeignKey(SubQuestion, on_delete=models.CASCADE, related_name='options')
    option_label = models.CharField(max_length=1, verbose_name="选项字母")
    option_content = models.TextField(verbose_name="选项内容")
    is_answer = models.BooleanField(default=False, verbose_name="是否为答案")

    def __str__(self):
        return f"{self.sub_question}-{self.option_label}"

# 连线题-右项表
class MatchingOption(models.Model):
    sub_question = models.ForeignKey(SubQuestion, on_delete=models.CASCADE, related_name='matchingOptions')
    option_label = models.CharField(max_length=1, verbose_name='选项字母', blank=False, null=False)
    option_content = models.TextField(verbose_name='选项内容')
    image_url = models.ImageField(verbose_name='选项图片', upload_to=images_upload_to, blank=True, null=True)

    def __str__(self):
        return f"{self.sub_question}-{self.option_label}"

# 改错题
class Correction(models.Model):
    CORRECTION_TYPES = [
        ('insert', '插入'),
        ('delete', '删除'),
        ('revise', '修改')
    ]
    sub_question = models.ForeignKey(SubQuestion, on_delete=models.CASCADE, related_name='corrections')
    type = models.CharField(max_length=10, choices=CORRECTION_TYPES, default='insert', verbose_name='改错类型')
    index = models.IntegerField(default=0, verbose_name='修改位置')

    def __str__(self):
        return f"{self.sub_question}-{self.type}"


class Blank(models.Model):
    sub_question = models.ForeignKey(SubQuestion, on_delete=models.CASCADE, related_name='blanks')
    index = models.IntegerField(default=0, verbose_name='填空位置')


# 单元表
class Unit(models.Model):
    TYPES = [
        ('practice', '练习'),
        ('exam', '考试'),
        ('task',' 作业'),
        ('quiz', '小测')
    ]
    class_instance = models.ForeignKey(Class, on_delete=models.CASCADE, related_name='units')
    order = models.IntegerField(verbose_name='单元序号', blank=False, null=False)
    title = models.CharField(verbose_name='单元名称', blank=True, null=True, max_length=100)
    type = models.CharField(verbose_name='题目类型', choices=TYPES, default='practice', blank=False, null=False, max_length=20)

class PaperPage(models.Model):
    unit = models.ForeignKey(Unit, on_delete=models.CASCADE, related_name='paper_pages')
    order = models.IntegerField(verbose_name='页面顺序', blank=False, null=False)
    text = models.TextField(verbose_name='页面文本', blank=True, null=True)
    created_at = models.DateTimeField(verbose_name='创建时间', auto_now_add=True)

class PageMainQuestion(models.Model):
    page = models.ForeignKey(PaperPage, on_delete=models.CASCADE, related_name='page_main_questions')
    main_question = models.ForeignKey(MainQuestion, on_delete=models.CASCADE, related_name='selected_main_questions')

class PageSubQuestion(models.Model):
    page_main_question = models.ForeignKey(PageMainQuestion, on_delete=models.CASCADE, related_name='page_sub_questions')
    sub_question = models.ForeignKey(SubQuestion, on_delete=models.CASCADE, related_name='selected_sub_questions')

class TimeManagement(models.Model):
    unit = models.ForeignKey(Unit, on_delete=models.CASCADE, related_name='time_management')
    week = models.IntegerField(verbose_name='开放周次', default=0)
    exam_date = models.DateField(verbose_name='考试日期', blank=True, null=True)
    start_time = models.TimeField(blank=True, null=True)
    end_time = models.TimeField(blank=True, null=True)
    duration = models.IntegerField(verbose_name='时长限制', blank=True, null=True)



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





