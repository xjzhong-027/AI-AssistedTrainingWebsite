from django.core.validators import MinValueValidator, MaxValueValidator
from django.db import models
from ELW.models import (
Unit,MediaMaterial,
MainQuestion,SubQuestion,ChoiceOption,
MatchingOption,Correction,PaperPage,TimeManagement
)
from Account.models import Students, Class


class StudentExamRecord(models.Model):
    user = models.ForeignKey(Students, on_delete=models.CASCADE)
    exam = models.ForeignKey(Unit, on_delete=models.CASCADE)
    started_at = models.DateTimeField(auto_now_add=True)
    ended_at = models.DateTimeField(null=True, blank=True)
    finished_at = models.DateTimeField(null=True, blank=True)
    submitted = models.BooleanField(default=False)
    score = models.DecimalField(verbose_name='总分', max_digits=5, decimal_places=1, null=True, blank=True)


class StudentPageRecord(models.Model):
    student_exam_record = models.ForeignKey(StudentExamRecord, on_delete=models.CASCADE, related_name='page_records')
    page = models.ForeignKey(PaperPage, on_delete=models.CASCADE, related_name='student_records')
    submitted = models.BooleanField(default=False)
    submitted_at = models.DateTimeField(null=True, blank=True)
    is_expired = models.BooleanField(default=False)  # 页面是否已超时
    remaining_time = models.FloatField(default=0)  # 剩余时间（分钟）
    integrity_score = models.DecimalField(verbose_name='诚信分', max_digits=2, decimal_places=1, default=1, validators=[
            MinValueValidator(0),  # 最小值为0
            MaxValueValidator(1)   # 最大值为1
        ])
    page_score = models.DecimalField(verbose_name='页面总分', max_digits=5, decimal_places=1, null=True, blank=True)

    def __str__(self):
        return f"Record for {self.student_exam_record.user} on Page {self.page.order}"


class StudentAnswer(models.Model):
    sub_question = models.ForeignKey(SubQuestion, on_delete=models.CASCADE, related_name='answers')
    student_page_record = models.ForeignKey(StudentPageRecord, on_delete=models.CASCADE, related_name='answers')
    text = models.TextField(verbose_name='答案文本', blank=True,null=True, default='')
    index = models.IntegerField(verbose_name='索引', blank=True, null=True)
    type = models.CharField(verbose_name='改错类型', max_length=50, blank=True, null=True)
    score = models.DecimalField(verbose_name='小题得分', max_digits=5, decimal_places=1, null=True, blank=True)


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