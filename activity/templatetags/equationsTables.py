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
    

@register.filter(name='totalHerramienta')
def totalHerramienta(herramienta):
    try:
        total = Decimal('0')
        for h in herramienta:
            total += h.herramienta.costodia * h.rendimiento
        return total
    except Exception:
        return Decimal('0')
    
@register.filter(name='totalEquipo')
def totalEquipo(equipo):
    try:
        total = Decimal('0')
        for e in equipo:
            total += e.equipo.costodia * e.rendimiento
        return total
    except Exception:
        return Decimal('0')
    
@register.filter(name='totalRiesgo')
def totalRiesgo(riesgo):
    try:
        total = Decimal('0')
        for r in riesgo:
            total += r.costo
        return total
    except Exception:
        return Decimal('0')
    
@register.filter(name='totalCalidad')
def totalCalidad(calidad):
    try:
        total = Decimal('0')
        for c in calidad:
            total += c.cantidad * c.calidad.precio
        return total
    except Exception:
        return Decimal('0')
    
@register.filter(name='totalAmbiental')
def totalAmbiental(ambiental):
    try:
        total = Decimal('0')
        for a in ambiental:
            total += a.valor
        return total
    except Exception:
        return Decimal('0')
    

@register.filter(name='totalHidrologica')
def totalHidrologica(hidrologica):
    try:
        total = Decimal('0')
        for h in hidrologica:
            total += h.costo
        return total
    except Exception:
        return Decimal('0')