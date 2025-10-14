# core/templatetags/core_extras.py
from django import template
from django.utils.safestring import mark_safe
from decimal import Decimal

register = template.Library()

@register.filter 
def multiplica(value, arg):
    try:
        return float(value) * float(arg)
    except (TypeError, ValueError):
        return ''

@register.filter(name='totalMateriales')
def totalMateriales(materials):
    try:
        total = Decimal('0')
        for m in materials:
            price = Decimal(str(m.material.price or 0))
            qty = Decimal(str(m.quantity or 0))
            total += price * qty
        return total
    except Exception:
        return Decimal('0')