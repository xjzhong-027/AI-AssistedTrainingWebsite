from django import template

register = template.Library()

@register.filter
def index_to_letter(index):
    try:
        letters = ["A", "B", "C", "D", "E", "F", "G", "H", "I", "J", "K", "L", "M","N"]
        return letters[int(index)]
    except (IndexError, ValueError):
        return ''
