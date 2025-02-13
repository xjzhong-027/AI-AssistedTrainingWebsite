from django.db import models
from ELW.models import Students


class Exam(models.Model):
    name = models.CharField(max_length=255)
    description = models.TextField(null=True, blank=True)
    start_time = models.DateTimeField()
    end_time = models.DateTimeField()
    duration_minutes = models.IntegerField()

class StudentExamRecord(models.Model):
    user = models.ForeignKey(Students, on_delete=models.CASCADE)
    exam = models.ForeignKey(Exam, on_delete=models.CASCADE)
    started_at = models.DateTimeField(auto_now_add=True)
    ended_at = models.DateTimeField(null=True, blank=True)
    finished_at = models.DateTimeField(null=True, blank=True)
    submitted = models.BooleanField(default=False)


class MediaMaterial(models.Model):
    title = models.TextField(default='')
    media_url = models.CharField(max_length=100,null=True, blank=True)

    def __str__(self):
        return self.title

class MainQuestion(models.Model):
    QUESTION_TYPES = [
        ('choice', '选择题'),
        ('matching', '连线题'),
        ('correction', '改错题'),
        ('comprehension', '主观题'),
    ]
    question_type = models.CharField(max_length=20, choices=QUESTION_TYPES, default='choice', verbose_name="题目类型")
    media_material = models.ForeignKey(MediaMaterial, on_delete=models.CASCADE, related_name='main_questions')
    question_text = models.TextField(verbose_name="大题题干", blank=False)  # 存储题干
    maximum_play = models.IntegerField(default=3)

    def __str__(self):
        return self.question_text

class SubQuestion(models.Model):
    main_question = models.ForeignKey(MainQuestion, on_delete=models.CASCADE, related_name='sub_questions')
    question_text = models.TextField(verbose_name='小题内容', blank=False, null=False)
    answer = models.TextField(verbose_name='参考答案', default='test', blank=False)
    score = models.FloatField(verbose_name='分数', default=1.0)

    def __str__(self):
        return f"{self.main_question} - {self.question_text[:20]}"



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


class Page(models.Model):
    exam = models.ForeignKey(Exam, on_delete=models.CASCADE, related_name='pages')
    main_questions = models.ManyToManyField(MainQuestion, related_name='pages')
    page_number = models.IntegerField(verbose_name="页码")
    can_modify = models.BooleanField(default=True)

    def __str__(self):
        return f"Page {self.page_number} of {self.exam.name}"

class StudentPageRecord(models.Model):
    student_exam_record = models.ForeignKey(StudentExamRecord, on_delete=models.CASCADE, related_name='page_records')
    page = models.ForeignKey(Page, on_delete=models.CASCADE, related_name='student_records')
    submitted = models.BooleanField(default=False)
    submitted_at = models.DateTimeField(null=True, blank=True)

    def __str__(self):
        return f"Record for {self.student_exam_record.user} on Page {self.page.page_number}"


class StudentAnswer(models.Model):
    sub_question = models.ForeignKey(SubQuestion, on_delete=models.CASCADE, related_name='answers')
    student_page_record = models.ForeignKey(StudentPageRecord, on_delete=models.CASCADE, related_name='answers')
    text = models.TextField(verbose_name='答案文本', blank=True,null=True, default='')
    #修改text答案文本

    def __str__(self):
        return f"Answer to {self.sub_question} by {self.student_page_record.student_exam_record.user}"


class StudentMediaPlayRecord(models.Model):
    student_exam_record = models.ForeignKey(StudentExamRecord, on_delete=models.CASCADE)
    main_question = models.ForeignKey(MainQuestion, on_delete=models.CASCADE)
    media_material = models.ForeignKey(MediaMaterial, on_delete=models.CASCADE,blank=True,null=True)  # 新增字段
    play_count = models.IntegerField(default=0)
    last_pause_time = models.FloatField(default=0)

    def __str__(self):
        return f"Play record for {self.student_exam_record.user} on {self.main_question}"

    class Meta:
        unique_together = ('student_exam_record', 'main_question', 'media_material')