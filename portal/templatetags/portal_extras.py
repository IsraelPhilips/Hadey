# portal/templatetags/portal_extras.py

from django import template

register = template.Library()

@register.filter(name='split')
def split(value, key):
    """
    Returns the value turned into a list.
    Usage: {{ some_string|split:"," }}
    """
    return value.split(key)

@register.filter(name='get_item')
def get_item(dictionary, key):
    """
    Returns the value of a dictionary key.
    Usage: {{ my_dict|get_item:my_variable }}
    """
    return dictionary.get(key)
