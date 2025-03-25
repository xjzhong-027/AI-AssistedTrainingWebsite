from django import template

register = template.Library()

@register.filter
def add_one(value):
    """将值加 1"""
    return value + 1

# @register.filter
# def custom_slice(value, arg):
#     """
#     自定义切片过滤器
#     :param value: 输入的列表
#     :param arg: 切片的范围，格式为 "start:end"
#     :return: 切片后的列表
#     """
#     try:
#         parts = arg.split(':')
#         start = int(parts[0]) if parts[0] else 0
#         end = int(parts[1]) if len(parts) > 1 and parts[1] else len(value)
#         return value[start:end]
#     except (ValueError, AttributeError, IndexError):
#         return value

@register.filter
def custom_before(value, index):
    """
    自定义 before 过滤器
    :param value: 输入的列表
    :param index: 截取的结束位置
    :return: 从开头到 index 的列表片段
    """
    try:
        index = int(index)
        return value[:index]
    except (ValueError, IndexError):
        return value

@register.filter
def custom_after(value, index):
    """
    自定义 after 过滤器
    :param value: 输入的列表
    :param index: 截取的起始位置
    :return: 从 index 到结尾的列表片段
    """
    try:
        index = int(index)
        return value[index:]
    except (ValueError, IndexError):
        return value

@register.filter
def split_image_urls(value):
    """
    自定义过滤器：将逗号分隔的图片 URL 字符串分割成列表
    :param value: 输入的字符串，例如 "/media/a.jpg, /media/b.jpg, /media/c.jpg"
    :return: 分割后的 URL 列表，例如 ["/media/a.jpg", "/media/b.jpg", "/media/c.jpg"]
    """
    if value:
        # print(f"url: {[url.strip() for url in value.split(',')]}")
        return [url.strip() for url in value.split(',') if url.strip()]
    return []