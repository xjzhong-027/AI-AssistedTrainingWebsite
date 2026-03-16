"""
周度周期工具函数。
以周一为 period_start，周日为 period_end。
"""
from datetime import date, timedelta
from typing import Tuple


def get_week_period(d: date) -> Tuple[date, date]:
    """
    根据任意日期，返回该日期所在周的周一和周日。

    Args:
        d: 任意日期

    Returns:
        (period_start, period_end) 周一和周日
    """
    # weekday(): Monday=0, Sunday=6
    days_since_monday = d.weekday()
    period_start = d - timedelta(days=days_since_monday)
    period_end = period_start + timedelta(days=6)
    return period_start, period_end


def parse_period_param(period_str: str) -> Tuple[date, date]:
    """
    解析 YYYY-MM-DD 格式的周期参数，返回该日期所在周的周一和周日。

    Args:
        period_str: 日期字符串，如 "2026-03-01"

    Returns:
        (period_start, period_end)

    Raises:
        ValueError: 格式无效时
    """
    try:
        d = date.fromisoformat(period_str)
    except ValueError as e:
        raise ValueError(f"无效的日期格式，应为 YYYY-MM-DD: {period_str}") from e
    return get_week_period(d)
