from django import template

register = template.Library()

@register.filter
def safe_getattr(value, arg):
    return getattr(value, arg, '')
