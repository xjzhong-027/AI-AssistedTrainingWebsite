from django.db import models
from django.contrib.auth.models import User, Group
from django.contrib.auth.models import AbstractUser



User._meta.verbose_name = '账号'
User._meta.verbose_name_plural = '所有账号'
Group._meta.verbose_name_plural = '分组'


class Admins(models.Model):
    """ 管理员 """
    username = models.CharField(verbose_name='用户名', max_length=32, unique=True)
    password = models.TextField(verbose_name='密码')
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='admins', null=True, blank=True)

    class Meta:
        verbose_name_plural = '管理员账号'

    def __str__(self):
        return self.username


class Teachers(models.Model):
    """ 教师账号 """
    username = models.CharField(max_length=20, verbose_name='账号', unique=True)
    name = models.CharField(max_length=20, verbose_name='姓名')
    password = models.CharField(max_length=100, verbose_name='密码')
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='teachers', null=True, blank=True)

    class Meta:
        verbose_name_plural = '教师账号'

    def __str__(self):
        return self.name


class Course(models.Model):
    """ 课程表 """
    grades = [
        ('1', '大一'),
        ('2', '大二'),
        ('3', '大三'),
        ('4', '大四')
    ]
    semesters = [
        ('上', '上学期'),
        ('下', '下学期'),
    ]
    year = models.IntegerField(verbose_name='开课年份', blank=False, null=False)
    grade = models.CharField(verbose_name='开课年级', choices=grades, max_length=30, blank=False, null=False)
    semester = models.CharField(verbose_name='开课学期', choices=semesters, max_length=30, blank=False, null=False)

    class Meta:
        verbose_name_plural = '课程'

    def __str__(self):
        return f"{self.year} - {self.grade} - {self.semester}"


class Class(models.Model):
    """ 班级表 """
    class_name = models.CharField(verbose_name='班级名称', max_length=200, null=True, blank=True)
    course = models.ForeignKey(Course, verbose_name='课程', on_delete=models.CASCADE, related_name="course_id")
    teacher = models.ForeignKey(Teachers, verbose_name='授课教师', on_delete=models.CASCADE, related_name="teacher_id")
    start_date = models.CharField(verbose_name='开课日期', blank=True, null=True, max_length=20)
    week = models.IntegerField(verbose_name='周几上课', blank=False, null=False, choices=[(1, '周一'), (2, '周二'), (3, '周三'), (4, '周四'), (5, '周五'), (6, '周六'), (7, '周日')])
    start_time = models.CharField(verbose_name='上课时间', blank=False, null=False, max_length=50)
    end_time = models.CharField(verbose_name='下课时间', blank=False, null=False, max_length=50)

    class Meta:
        verbose_name_plural = '班级'

    def __str__(self):
        return f"Class {self.class_name}"


class Students(models.Model):
    """ 学生表 """
    class_instance = models.ForeignKey(Class, verbose_name='班级', on_delete=models.CASCADE, related_name='class_id')
    username = models.CharField(verbose_name='学生账号', max_length=20, unique=True)
    name = models.CharField(verbose_name='学生姓名', max_length=20)
    password = models.CharField(verbose_name='学生密码', max_length=100)
    seat_number = models.CharField(verbose_name='座位号', max_length=10, null=True, blank=True)
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name="students", null=True, blank=True)

    class Meta:
        verbose_name_plural = '学生账号'

    def __str__(self):
        return f"{self.name} - {self.class_instance}"


class ClassScheduleAdjustment(models.Model):
    """ 调课记录 """
    class_instance = models.ForeignKey(Class, on_delete=models.CASCADE, related_name="schedule_adjustments")  # 关联班级
    week = models.IntegerField(blank=False, null=False)  # 该调整适用的周次
    new_week_day = models.IntegerField(blank=False, null=False,choices=[(1, '周一'), (2, '周二'), (3, '周三'), (4, '周四'), (5, '周五'), (6, '周六'), (7, '周日')])  # 调整后的上课星期
    new_class_begin_time = models.CharField(blank=False, null=False, max_length=50)  # 调整后的上课时间
    new_class_end_time = models.CharField(blank=False, null=False, max_length=50) # 调整后的下课时间

    def __str__(self):
        return f"{self.class_instance.class_name} - Week {self.week} - 周{self.new_week_day} {self.new_class_begin_time}"

class ClassScheduleAddition(models.Model):
    """ 补课记录 """
    class_instance = models.ForeignKey(Class, on_delete=models.CASCADE, related_name="schedule_additions")  # 关联班级
    week = models.IntegerField(blank=False, null=False)  # 上课周次
    weekday = models.IntegerField(blank=False, null=False, choices=[(1, '周一'), (2, '周二'), (3, '周三'), (4, '周四'), (5, '周五'), (6, '周六'), (7, '周日')])  # 上课星期
    class_begin_time = models.CharField(blank=False, null=False, max_length=50)  # 上课时间
    class_end_time = models.CharField(blank=False, null=False, max_length=50)  # 下课时间

    def __str__(self):
        return f"{self.class_instance.class_name} - Week {self.week} - 周{self.weekday} {self.class_begin_time}"

class Attendance(models.Model):
    """ 学生考勤记录表 """
    student = models.ForeignKey(Students, verbose_name='学生', on_delete=models.CASCADE, related_name="student_id")
    week = models.IntegerField(verbose_name='周次', blank=False, null=False)
    status = models.CharField(
        verbose_name='考勤状况', blank=False, null=False, max_length=20,
        choices=[('normal', '正常出勤'), ('absent', '缺勤'), ('late', '迟到'), ('early-leave', '早退'), ('abnormal', '异常挂机'), ('late and early-leave', '迟到+早退'), ('vacation', '假期')],
        default='absent',
    )
    adjusted_class_time = models.ForeignKey(ClassScheduleAdjustment, verbose_name='调课记录', on_delete=models.SET_NULL, null=True, blank=True)
    added_class_time = models.ForeignKey(ClassScheduleAddition, verbose_name='补课记录', on_delete=models.CASCADE, null=True, blank=True)

    class Meta:
        verbose_name_plural = '考勤记录'

    def __str__(self):
        return f"{self.student.name} - Week {self.week} - {self.status}"

