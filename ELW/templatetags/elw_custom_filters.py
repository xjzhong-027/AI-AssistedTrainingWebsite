from django import template

register = template.Library()

@register.filter
def add_one(value):
    """将值加 1"""
    return value + 1


@register.filter
def custom_slice(value, arg):
    """
    自定义切片过滤器
    :param value: 输入的列表
    :param arg: 切片的范围，格式为 "start:end"
    :return: 切片后的列表
    """
    try:
        parts = arg.split(':')
        start = int(parts[0]) if parts[0] else 0
        end = int(parts[1]) if len(parts) > 1 and parts[1] else len(value)
        return value[start:end]
    except (ValueError, AttributeError, IndexError):
        return value