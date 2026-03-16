"""
Common 模块数据模型。
"""
from django.db import models
from Account.models import Students


class StudentBehaviorWeeklyScore(models.Model):
    """
    学生周度行为评分表（BSA-IFM 模型）。
    存储每周计算的形成性评估综合分 F、参与度分 P 及各维度分。
    """
    student = models.ForeignKey(
        Students,
        on_delete=models.CASCADE,
        related_name='behavior_weekly_scores',
        verbose_name='学生'
    )
    period_start = models.DateField(verbose_name='统计周期开始（周一）')
    period_end = models.DateField(verbose_name='统计周期结束（周日）')

    # 维度分（0-100）
    S_A = models.DecimalField(
        verbose_name='正确率与用时维度',
        max_digits=5,
        decimal_places=2,
        null=True,
        blank=True
    )
    S_B = models.DecimalField(
        verbose_name='出勤与投入维度',
        max_digits=5,
        decimal_places=2,
        null=True,
        blank=True
    )
    S_C = models.DecimalField(
        verbose_name='专注与用时偏差维度',
        max_digits=5,
        decimal_places=2,
        null=True,
        blank=True
    )
    S_D = models.DecimalField(
        verbose_name='提示使用维度',
        max_digits=5,
        decimal_places=2,
        null=True,
        blank=True
    )

    F_score = models.DecimalField(
        verbose_name='综合形成性评分',
        max_digits=5,
        decimal_places=2,
        null=True,
        blank=True
    )
    P_score = models.DecimalField(
        verbose_name='参与度分',
        max_digits=5,
        decimal_places=2,
        null=True,
        blank=True
    )
    growth_bonus = models.SmallIntegerField(
        verbose_name='成长奖励分',
        default=0,
        null=True,
        blank=True
    )

    created_at = models.DateTimeField(auto_now_add=True, verbose_name='创建时间')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='更新时间')

    class Meta:
        db_table = 'student_behavior_score'
        verbose_name = '学生周度行为评分'
        verbose_name_plural = '学生周度行为评分'
        unique_together = [('student', 'period_start')]
        ordering = ['-period_start']
        indexes = [
            models.Index(fields=['student']),
            models.Index(fields=['period_start']),
            models.Index(fields=['F_score']),
        ]

    def __str__(self):
        return f"{self.student.name} - {self.period_start} - F={self.F_score}"
