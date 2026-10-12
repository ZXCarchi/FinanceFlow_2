from django import template
from django.utils.translation import gettext as _
register = template.Library()
CATEGORY_LABELS = {'food':'Food','transport':'Transport','housing':'Housing','utilities':'Utilities','entertainment':'Entertainment','education':'Education','health':'Health','shopping':'Shopping','subscriptions':'Subscriptions','salary':'Salary','part-time':'Part-time work','scholarship':'Scholarship','freelance':'Freelance','other':'Other'}
@register.filter
def category_label(category):
    if not category: return _('Uncategorized')
    return _(CATEGORY_LABELS.get(category.code, category.name))
@register.filter
def money(value):
    try: return f'{float(value):,.2f}'.replace(',', ' ')
    except Exception: return value
