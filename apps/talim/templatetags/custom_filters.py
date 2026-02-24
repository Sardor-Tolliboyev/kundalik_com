# apps/talim/templatetags/custom_filters.py
from django import template

register = template.Library()

@register.filter(name='get_item')
def get_item(dictionary, key):
    """Lug'atdan kalit orqali qiymatni olish filtri"""
    if dictionary:
        return dictionary.get(key)
    return None