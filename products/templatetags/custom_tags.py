from django import template

register = template.Library()

@register.filter
def custom_range(value):
    return range(1, value + 1)
