from django.contrib.auth.models import User
from django.db import models

from django.db.models.signals import post_migrate, pre_delete
from django.dispatch import receiver

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
    is_default = models.BooleanField(default=False, verbose_name="是否默认规则")

    class Meta:
        verbose_name = "逾期扣分规则"
        verbose_name_plural = "逾期扣分规则"
        constraints = [
            models.UniqueConstraint(
                fields=['is_default'],
                condition=models.Q(is_default=True),
                name='unique_default_rule'
            )
        ]

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


# 创建默认规则的信号
@receiver(post_migrate)
def create_default_rule(sender, **kwargs):
    if sender.name == 'Query':
        if not OverdueDeductionRule.objects.filter(is_default=True).exists():
            default_rule = OverdueDeductionRule.objects.create(
                rule_name="默认逾期扣分规则",
                description="默认规则：每超期一周增扣10%，最多扣100%",
                is_default=True,
                is_active=True
            )

            # 创建10个时间段（每周一个）
            for week in range(1, 11):
                OverduePeriod.objects.create(
                    rule=default_rule,
                    period_name=f"超期第{week}周",
                    min_days=(week - 1) * 7,
                    max_days=week * 7 if week < 10 else None,
                    deduction_rate=round(1 - week * 0.1, 2),  # 0.9, 0.8,...,0
                    description=f"超期{week}周，扣分{week * 10}%"
                )

# 不能删除默认规则
@receiver(pre_delete, sender=OverdueDeductionRule)
def prevent_default_rule_delete(sender, instance, **kwargs):
    if instance.is_default:
        raise Exception("默认规则不能删除")