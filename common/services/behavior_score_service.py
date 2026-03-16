"""
BSA-IFM 行为评分计算服务。
纯函数实现，与 Django 解耦，便于单元测试。
"""
from typing import Dict, List, Any

# 论文权重与阈值常量（后续可抽到配置）
FAST_RATIO_THRESHOLD = 0.4  # 用时 < 参考时间*0.4 视为过快
GROWTH_BONUS_20 = 5
GROWTH_BONUS_10 = 3


def calc_S_acc(correct_answers: int, total_answers: int) -> float:
    """正确率 S_acc (0-100)。"""
    if total_answers == 0:
        return 0.0
    return (correct_answers / total_answers) * 100


def calc_S_time(fast_answers: int, total_answers: int) -> float:
    """过快惩戒分 S_time (0-100)，无题目时不扣分。"""
    if total_answers == 0:
        return 100.0
    p_fast = fast_answers / total_answers
    return 100 - 100 * p_fast


def calc_S_attend(on_time: int, late: int, expected_sessions: int) -> float:
    """出勤准时率 S_attend (0-100)。"""
    if expected_sessions == 0:
        return 100.0
    weighted = on_time + 0.5 * late
    return min(100.0, (weighted / expected_sessions) * 100)


def calc_S_duration(actual_seconds: float, expected_minutes: float) -> float:
    """有效学习时长得分 S_duration (0-100)。"""
    if expected_minutes == 0:
        return 0.0
    expected_seconds = expected_minutes * 60
    ratio = actual_seconds / expected_seconds
    return min(100.0, ratio * 100)


def calc_S_complete(completed_questions: int, expected_questions: int) -> float:
    """任务完成率 S_complete (0-100)。"""
    if expected_questions == 0:
        return 100.0
    ratio = completed_questions / expected_questions
    return min(100.0, ratio * 100)


def calc_S_focus(p_idle: float) -> float:
    """鼠标停滞比例 S_focus (60-100)。暂缺数据时返回 100。"""
    if p_idle is None or p_idle < 0:
        return 100.0
    return 100 - min(p_idle * 100, 40)


def _time_deviation_score(time_spent: float, ref_time: float) -> float:
    """单题用时偏差得分。"""
    if ref_time is None or ref_time <= 0:
        return 100.0
    r = time_spent / ref_time
    if 0.8 <= r <= 1.2:
        return 100.0
    if 0.6 <= r < 0.8 or 1.2 < r <= 1.4:
        return 80.0
    return 60.0


def calc_S_timedev(answers: List[Dict[str, Any]]) -> float:
    """答题用时偏差度 S_timedev (0-100)。"""
    if not answers:
        return 100.0
    total = 0.0
    for ans in answers:
        total += _time_deviation_score(
            ans.get('time_spent', 0) or 0,
            ans.get('ref_time')
        )
    return total / len(answers)


def calc_S_AI(ai_hint_count: int, total_answers: int) -> float:
    """AI 提示使用得分 S_AI (0-100)。"""
    if total_answers == 0:
        return 0.0
    avg = ai_hint_count / total_answers
    if avg == 0:
        return 75.0
    if avg <= 1:
        return 100.0
    if avg <= 2:
        return 85.0
    return 50.0


def calc_S_blank(blank_hint_count: int, total_answers: int) -> float:
    """填空提示使用得分 S_blank (0-100)。"""
    if total_answers == 0:
        return 0.0
    avg = blank_hint_count / total_answers
    if avg == 0:
        return 75.0
    if avg <= 1:
        return 100.0
    return 60.0


def calc_growth_bonus(recent_avg: float, previous_avg: float) -> int:
    """成长奖励分 G (0/3/5)。"""
    if previous_avg == 0:
        return 0
    increase = (recent_avg - previous_avg) / previous_avg * 100
    if increase >= 20:
        return GROWTH_BONUS_20
    if increase >= 10:
        return GROWTH_BONUS_10
    return 0


def compute_behavior_scores(stats: Dict[str, Any]) -> Dict[str, float]:
    """
    根据 StudentWeeklyRawStats 计算 BSA-IFM 各维度分与总分。

    Args:
        stats: 包含 total_answers, correct_answers, fast_answers, on_time, late,
               expected_sessions, actual_learning_seconds, expected_learning_minutes,
               completed_questions, expected_questions, ai_hint_count, blank_hint_count,
               answer_time_details, recent_avg, previous_avg 等

    Returns:
        S_A, S_B, S_C, S_D, F_score, P_score, growth_bonus
    """
    total_answers = stats.get('total_answers', 0) or 0
    correct_answers = stats.get('correct_answers', 0) or 0
    fast_answers = stats.get('fast_answers', 0) or 0

    S_acc = calc_S_acc(correct_answers, total_answers)
    S_time = calc_S_time(fast_answers, total_answers)
    S_A = 0.85 * S_acc + 0.15 * S_time

    on_time = stats.get('on_time', 0) or 0
    late = stats.get('late', 0) or 0
    expected_sessions = stats.get('expected_sessions', 0) or 0
    actual_seconds = stats.get('actual_learning_seconds', 0) or 0
    expected_minutes = stats.get('expected_learning_minutes', 0) or 0
    completed_questions = stats.get('completed_questions', 0) or 0
    expected_questions = stats.get('expected_questions', 0) or 0

    S_attend = calc_S_attend(on_time, late, expected_sessions)
    S_duration = calc_S_duration(actual_seconds, expected_minutes)
    S_complete = calc_S_complete(completed_questions, expected_questions)
    S_B = 0.40 * S_attend + 0.35 * S_duration + 0.25 * S_complete

    # S_focus 暂缺数据，取 100
    S_focus = 100.0
    answer_details = stats.get('answer_time_details', []) or []
    S_timedev = calc_S_timedev(answer_details)
    S_C = 0.50 * S_focus + 0.50 * S_timedev

    ai_hint_count = stats.get('ai_hint_count', 0) or 0
    blank_hint_count = stats.get('blank_hint_count', 0) or 0
    S_AI = calc_S_AI(ai_hint_count, total_answers)
    S_blank = calc_S_blank(blank_hint_count, total_answers)
    S_D = 0.60 * S_AI + 0.40 * S_blank

    recent_avg = stats.get('recent_avg', 0) or 0
    previous_avg = stats.get('previous_avg', 0) or 0
    G = calc_growth_bonus(recent_avg, previous_avg)

    F = 0.40 * S_A + 0.25 * S_B + 0.20 * S_C + 0.15 * S_D + G
    F = min(F, 100.0)

    P = 0.45 * S_B + 0.30 * S_C + 0.25 * S_D

    return {
        'S_A': round(S_A, 2),
        'S_B': round(S_B, 2),
        'S_C': round(S_C, 2),
        'S_D': round(S_D, 2),
        'F_score': round(F, 2),
        'P_score': round(P, 2),
        'growth_bonus': G,
    }
