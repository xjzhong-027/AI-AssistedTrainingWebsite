from django import template

register = template.Library()

@register.filter
def get_item(dictionary, key):
    if isinstance(dictionary, dict):
        return dictionary.get(key)
    return None


@register.filter
def split(value, arg):
    return value.split(arg)

@register.filter
def parse_correction_answer(value):
    if not value or value == "right":
        return {"type": "", "index": "", "text": value}
    try:
        parts = value.split(":")
        return {"type": parts[0], "index": parts[1], "text": parts[2]}
    except (ValueError, IndexError):
        return {"type": "", "index": "", "text": ""}