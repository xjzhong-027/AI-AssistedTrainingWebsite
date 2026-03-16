"""
周度行为评分计算任务。
"""
from datetime import date, datetime
from typing import Set

from common.utils.date_utils import get_week_period
from common.services.behavior_aggregation_service import get_student_weekly_raw_stats
from common.services.behavior_score_service import compute_behavior_scores
from common.models import StudentBehaviorWeeklyScore


def _get_student_ids_for_period(period_start: date, period_end: date) -> Set[int]:
    """获取需计算的学生 ID：本周有学习行为的 + 所有在籍学生（确保各班都有排名数据）。"""
    from accessment.models import StudentExamRecord
    from Account.models import Students

    start_dt = datetime.combine(period_start, datetime.min.time())
    end_dt = datetime.combine(period_end, datetime.max.time().replace(microsecond=0))

    ids_from_exam = set(
        StudentExamRecord.objects.filter(
            started_at__gte=start_dt,
            started_at__lte=end_dt,
        ).values_list('user_id', flat=True).distinct()
    )
    ids_from_students = set(Students.objects.values_list('id', flat=True))
    return ids_from_exam | ids_from_students


def calculate_weekly_behavior_scores(period_start: date) -> int:
    """
    计算指定周所有学生的行为评分并写入数据库。

    Args:
        period_start: 统计周期开始（周一）

    Returns:
        更新的记录数
    """
    period_end = get_week_period(period_start)[1]
    student_ids = _get_student_ids_for_period(period_start, period_end)
    count = 0

    for sid in student_ids:
        stats = get_student_weekly_raw_stats(sid, period_start, period_end)
        scores = compute_behavior_scores(stats)

        _, created = StudentBehaviorWeeklyScore.objects.update_or_create(
            student_id=sid,
            period_start=period_start,
            defaults={
                'period_end': period_end,
                'S_A': scores['S_A'],
                'S_B': scores['S_B'],
                'S_C': scores['S_C'],
                'S_D': scores['S_D'],
                'F_score': scores['F_score'],
                'P_score': scores['P_score'],
                'growth_bonus': scores['growth_bonus'],
            }
        )
        count += 1

    return count
