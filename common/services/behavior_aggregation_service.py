"""
行为数据周度聚合服务。
从现有模型聚合出 StudentWeeklyRawStats，供 BSA-IFM 评分使用。
"""
from datetime import date, datetime
from typing import Dict, Any, List, Optional

from django.db.models import Sum


def _period_to_semester_week(period_start: date, class_start_str: Optional[str]) -> Optional[int]:
    """
    将日历周起始日映射为学期周次。
    class_start_str: Class.start_date，如 "2026-02-24"
    """
    if not class_start_str:
        return None
    try:
        start = datetime.strptime(class_start_str.strip()[:10], '%Y-%m-%d').date()
    except (ValueError, TypeError):
        return None
    delta = (period_start - start).days
    if delta < 0:
        return None
    return delta // 7 + 1


def get_student_weekly_raw_stats(
    student_id: int,
    period_start: date,
    period_end: date
) -> Dict[str, Any]:
    """
    为指定学生在指定周内聚合原始行为统计量。

    Args:
        student_id: 学生 ID
        period_start: 周期开始（周一）
        period_end: 周期结束（周日）

    Returns:
        StudentWeeklyRawStats 字典
    """
    from Account.models import Students, Class, Attendance
    from accessment.models import StudentExamRecord, StudentPageRecord, StudentAnswer
    from AI_module.models import HintRequestLog
    from ELW.models import TimeManagement

    period_start_dt = datetime.combine(period_start, datetime.min.time())
    period_end_dt = datetime.combine(period_end, datetime.max.time().replace(microsecond=0))

    student = Students.objects.filter(id=student_id).first()
    if not student:
        return _empty_stats(student_id, period_start, period_end)

    cls = getattr(student, 'class_instance', None)
    class_start = cls.start_date if cls else None
    semester_week = _period_to_semester_week(period_start, class_start)

    # 1. 答题与正确数：StudentAnswer + StudentPageRecord + StudentExamRecord
    page_records = StudentPageRecord.objects.filter(
        student_exam_record__user_id=student_id,
        student_exam_record__started_at__gte=period_start_dt,
        student_exam_record__started_at__lte=period_end_dt,
    ).values_list('id', flat=True)

    answers = StudentAnswer.objects.filter(student_page_record_id__in=page_records)
    total_answers = answers.count()
    correct_answers = answers.exclude(score__isnull=True).exclude(score=0).count()

    # 2. 练习完成情况
    exam_qs = StudentExamRecord.objects.filter(
        user_id=student_id,
        started_at__gte=period_start_dt,
        started_at__lte=period_end_dt,
    )
    total_practices = exam_qs.count()
    completed_practices = exam_qs.filter(submitted=True).count()

    total_questions = 0
    for rec in exam_qs.select_related('exam').prefetch_related('exam__paper_pages'):
        for page in rec.exam.paper_pages.all():
            for pmq in page.page_main_questions.all():
                total_questions += pmq.page_sub_questions.count()

    completed_questions = StudentAnswer.objects.filter(
        student_page_record__student_exam_record__user_id=student_id,
        student_page_record__student_exam_record__started_at__gte=period_start_dt,
        student_page_record__student_exam_record__started_at__lte=period_end_dt,
    ).count()

    # 3. 提示使用：HintRequestLog 无 ai/fill 区分，level>=2 视为 AI 类，否则填空类
    hint_qs = HintRequestLog.objects.filter(
        student_id=student_id,
        request_time__gte=period_start_dt,
        request_time__lte=period_end_dt,
    )
    ai_hint_count = hint_qs.filter(level__gte=2).count()
    blank_hint_count = hint_qs.filter(level__lt=2).count()

    # 4. 出勤：Attendance
    on_time = 0
    late = 0
    expected_sessions = 0
    if semester_week:
        att_qs = Attendance.objects.filter(student_id=student_id, week=semester_week)
        on_time = att_qs.filter(status='normal').count()
        late = att_qs.filter(status='late').count() + att_qs.filter(status='late and early-leave').count()
        expected_sessions = att_qs.count() or 1
    if expected_sessions == 0:
        expected_sessions = 1

    # 5. 有效学习时长与预期时长（简化）
    # 无 time_spent，用完成练习数 * 单次平均时长估算
    unit_ids = list(exam_qs.values_list('exam_id', flat=True))
    expected_minutes = 0
    if unit_ids:
        tm = TimeManagement.objects.filter(unit_id__in=unit_ids).aggregate(
            total=Sum('duration')
        )
        expected_minutes = tm['total'] or 0
    if expected_minutes == 0:
        expected_minutes = total_practices * 30  # 默认 30 分钟/次

    # 用完成题数 * 平均每题 2 分钟近似 actual_learning_seconds
    actual_learning_seconds = completed_questions * 120.0 if completed_questions else 0

    # 6. 过快作答、用时偏差：无每题 time_spent，暂不计算
    fast_answers = 0
    answer_time_details: List[Dict[str, Any]] = []

    # 7. 成长奖励：最近 6 次考试正确率
    recent_avg = 0.0
    previous_avg = 0.0
    exam_scores = list(
        StudentExamRecord.objects.filter(user_id=student_id)
        .exclude(score__isnull=True)
        .order_by('-started_at')
        .values_list('score', flat=True)[:6]
    )
    if len(exam_scores) >= 6:
        recent_avg = sum(float(s) for s in exam_scores[:3]) / 3
        previous_avg = sum(float(s) for s in exam_scores[3:6]) / 3
    elif len(exam_scores) >= 3:
        recent_avg = sum(float(s) for s in exam_scores[:3]) / 3

    # 总题数用于计算 expected_questions
    expected_questions = total_questions or 1

    return {
        'student_id': student_id,
        'period_start': period_start,
        'period_end': period_end,
        'total_answers': total_answers,
        'correct_answers': correct_answers,
        'fast_answers': fast_answers,
        'total_practices': total_practices,
        'completed_practices': completed_practices,
        'total_questions': total_questions,
        'completed_questions': completed_questions,
        'expected_questions': expected_questions,
        'ai_hint_count': ai_hint_count,
        'blank_hint_count': blank_hint_count,
        'on_time': on_time,
        'late': late,
        'expected_sessions': expected_sessions,
        'actual_learning_seconds': actual_learning_seconds,
        'expected_learning_minutes': expected_minutes,
        'answer_time_details': answer_time_details,
        'recent_avg': recent_avg,
        'previous_avg': previous_avg,
    }


def _empty_stats(student_id: int, period_start: date, period_end: date) -> Dict[str, Any]:
    return {
        'student_id': student_id,
        'period_start': period_start,
        'period_end': period_end,
        'total_answers': 0,
        'correct_answers': 0,
        'fast_answers': 0,
        'total_practices': 0,
        'completed_practices': 0,
        'total_questions': 0,
        'completed_questions': 0,
        'expected_questions': 1,
        'ai_hint_count': 0,
        'blank_hint_count': 0,
        'on_time': 0,
        'late': 0,
        'expected_sessions': 1,
        'actual_learning_seconds': 0,
        'expected_learning_minutes': 0,
        'answer_time_details': [],
        'recent_avg': 0.0,
        'previous_avg': 0.0,
    }
