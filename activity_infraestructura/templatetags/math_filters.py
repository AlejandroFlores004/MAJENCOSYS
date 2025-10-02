from django import template
from decimal import Decimal

register = template.Library()

@register.filter
def multiply(value, arg):
    try:
        return round(value * arg, 2)
    except (TypeError, ValueError):
        return 0

@register.filter
def sum_total_by_activity(materials, activity):
    """
    Suma el total de price * quantity de los materiales
    que pertenecen a una actividad específica.
    """
    try:
        total = Decimal('0.00')
        for m in materials:
            if (
                m.activity.id == activity.id and 
                m.material and 
                m.material.price is not None and 
                m.quantity is not None
            ):
                total += m.material.price * m.quantity
        return round(total, 2)
    except:
        return Decimal('0.00')
    
@register.filter
def cal_jornal_total(jornal, prestaciones):
    try:
        return round(jornal / (1 - prestaciones),2)
    except (TypeError, ValueError):
        return 0
    
@register.simple_tag
def sub_total_jornal(jornal, prestaciones,rendimiento):
    try:
        return round((jornal / (1 - prestaciones))/rendimiento, 2)
    except (TypeError, ValueError):
        return 0

@register.filter
def sum_total_labour_by_activity(labours, activity):
    """
    Suma el total de price * quantity de los materiales
    que pertenecen a una actividad específica.
    """
    try:
        total = Decimal('0.00')
        for m in labours:
            if (
                m.activity.id == activity.id and 
                m.labour
            ):
                total += (m.labour.price / (1- m.prestation)) / m.performance
        return round(total, 2)
    except:
        return Decimal('0.00')
    
@register.filter
def sum_total_tool_by_activity(tools, activity):
    """
    Suma el total de price * quantity de los materiales
    que pertenecen a una actividad específica.
    """
    try:
        total = Decimal('0.00')
        for t in tools:
            if (
                t.activity.id == activity.id and 
                t.tool and 
                t.tool.dayCost is not None and 
                t.performance is not None
            ):
                total += t.tool.dayCost * t.performance
        return round(total, 2)
    except:
        return Decimal('0.00')