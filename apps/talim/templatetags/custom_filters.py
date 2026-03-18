# apps/talim/templatetags/custom_filters.py
from django import template

register = template.Library()

@register.filter(name='get_item')
def get_item(lugat, kalit):
    """
    Django template'larda lug'atdan qiymat olish filtri.

    # IZOH: Template ichida `lugat[kalit]` yozish noqulay bo'lgani uchun kerak.
    Misol: `{{ oquvchi.tayyor_baholar|get_item:mavzu.id }}`
    """
    if lugat:
        return lugat.get(kalit)
    return None
