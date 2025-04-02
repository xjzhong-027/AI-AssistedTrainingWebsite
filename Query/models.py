from django.contrib.auth.models import User
from django.core.validators import MinValueValidator
from django.db import models
import uuid
import os
from Account.models import Class


""" ---------------------------------------- 考勤管理 --------------------------------------------"""
class ClassroomLayout(models.Model):
    """ 教室布局表 """
    class_instance = models.ForeignKey(Class, on_delete=models.CASCADE)
    seat_rows = models.IntegerField(null=True, blank=True)
    seat_cols = models.IntegerField(null=True, blank=True)

    def __str__(self):
        return f"Classroom for {self.class_instance}"




""" ---------------------------------------- 逾期扣分规则 --------------------------------------------"""

class OverdueDeductionRule(models.Model):
    """
    逾期扣分规则模型
    """
    rule_name = models.CharField(max_length=100, verbose_name="规则名称", unique=True)
    description = models.TextField(verbose_name="规则描述", blank=True)
    is_active = models.BooleanField(default=True, verbose_name="是否启用")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="创建时间")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="更新时间")

    class Meta:
        verbose_name = "逾期扣分规则"
        verbose_name_plural = "逾期扣分规则"

    def __str__(self):
        return self.rule_name


class OverduePeriod(models.Model):
    """
    逾期时间段及对应扣分比例
    """
    rule = models.ForeignKey(OverdueDeductionRule, on_delete=models.CASCADE, related_name="periods")
    period_name = models.CharField(max_length=50, verbose_name="时间段名称")
    min_days = models.IntegerField(verbose_name="最小天数")
    max_days = models.IntegerField(verbose_name="最大天数", null=True, blank=True)  # 为空表示无上限
    deduction_rate = models.DecimalField(
        max_digits=3,
        decimal_places=2,
        verbose_name="扣分比例",
        help_text="例如0.9表示扣10%，剩余90%"
    )
    description = models.TextField(verbose_name="描述", blank=True)

    class Meta:
        verbose_name = "逾期时间段"
        verbose_name_plural = "逾期时间段"
        ordering = ['min_days']

    def __str__(self):
        if self.max_days:
            return f"{self.period_name}({self.min_days}-{self.max_days}天): {self.deduction_rate}"
        return f"{self.period_name}({self.min_days}天以上): {self.deduction_rate}"