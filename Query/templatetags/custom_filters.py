from django import template

register = template.Library()

@register.filter
def get_item(dictionary, key):
    """模板过滤器：获取字典中给定键的值"""
    return dictionary.get(key)