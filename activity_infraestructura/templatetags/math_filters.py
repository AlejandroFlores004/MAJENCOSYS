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