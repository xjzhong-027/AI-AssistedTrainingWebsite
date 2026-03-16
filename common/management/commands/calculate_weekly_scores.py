"""
Django 管理命令：计算指定周的学生行为评分。

用法:
    python manage.py calculate_weekly_scores --period=2026-03-01
    python manage.py calculate_weekly_scores  # 默认使用今天所在周
"""
from datetime import date

from django.core.management.base import BaseCommand

from common.utils.date_utils import get_week_period, parse_period_param
from common.services.weekly_behavior_job import calculate_weekly_behavior_scores


class Command(BaseCommand):
    help = '计算指定周的学生行为评分（BSA-IFM 模型）'

    def add_arguments(self, parser):
        parser.add_argument(
            '--period',
            type=str,
            default=None,
            help='周期日期 YYYY-MM-DD，默认为今天所在周',
        )

    def handle(self, *args, **options):
        period_str = options.get('period')
        if period_str:
            try:
                period_start, period_end = parse_period_param(period_str)
            except ValueError as e:
                self.stderr.write(self.style.ERROR(str(e)))
                return
        else:
            today = date.today()
            period_start, period_end = get_week_period(today)

        self.stdout.write(f'计算周期: {period_start} ~ {period_end}')

        count = calculate_weekly_behavior_scores(period_start)
        self.stdout.write(self.style.SUCCESS(f'成功更新 {count} 条学生行为评分记录'))
