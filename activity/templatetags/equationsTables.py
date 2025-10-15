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
    
@register.filter 
def dividir(value, arg):
    try:
        return float(value) / float(arg)
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
    
@register.filter 
def jornalTotal(value, arg):
    try:
        return float(value) / (1-float(arg))
    except (TypeError, ValueError):
        return ''
    
@register.filter(name='totalManoObra')
def totalManoObra(manoObra):
    try:
        total = Decimal('0')
        for m in manoObra:
            jornadaTotal = m.manoobra.jornada / (1 - m.prestaciones)
            total += jornadaTotal / m.rendimiento
        return total
    except Exception:
        return Decimal('0')
    