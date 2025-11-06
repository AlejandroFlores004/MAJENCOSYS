# core/templatetags/core_extras.py
from django import template
from django.utils.safestring import mark_safe
from decimal import Decimal, InvalidOperation, DivisionByZero
from datetime import date, datetime, timedelta

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
def totalManoObra(manoObra, sched=None):
    """
    Suma: (jornada / (1 - prestaciones)) / rendimiento  de cada ítem,
    y multiplica el total por los días hábiles (lun–sáb) del schedule si se pasa.
    """
    try:
        total = Decimal('0')

        # Sumar todos los ítems primero
        for m in manoObra:
            try:
                jornada = Decimal(str(m.manoobra.jornada))
                prestaciones = Decimal(str(m.prestaciones))
                rendimiento = Decimal(str(m.rendimiento))

                # Evitar divisiones inválidas
                if rendimiento <= 0:
                    continue
                if prestaciones >= Decimal('1'):
                    continue

                jornada_total = jornada / (Decimal('1') - prestaciones)
                total += (jornada_total / rendimiento)
            except (InvalidOperation, DivisionByZero):
                continue

        # Multiplicar por días hábiles si recibimos schedule
        if sched is not None:
            start = getattr(sched, 'start_date', None)
            end = getattr(sched, 'end_date', None)
            if start and end:
                days = _count_mon_sat(_to_date(start), _to_date(end))
                total *= Decimal(days)

        return total
    except Exception:
        return Decimal('0')
    
def _to_date(d):
    if isinstance(d, datetime):
        return d.date()
    if isinstance(d, date):
        return d
    return date.fromisoformat(str(d))

def _count_mon_sat(start, end):
    if end < start:
        return 0
    d = start
    one = timedelta(days=1)
    count = 0
    while d <= end:
        # 0=lun ... 6=dom -> excluye 6
        if d.weekday() != 6:
            count += 1
        d += one
    return count

@register.filter(name="times_business_days")
def times_business_days(value, sched):
    """
    Multiplica 'value' por la cantidad de días hábiles (lun–sáb) entre
    sched.start_date y sched.end_date (ambos inclusive).
    """
    try:
        start = getattr(sched, "start_date", None)
        end = getattr(sched, "end_date", None)
        if not start or not end:
            return value  # si falta alguna fecha, no toca el valor

        start = _to_date(start)
        end = _to_date(end)

        days = _count_mon_sat(start, end)
        return float(value) * days
    except Exception:
        return value
    

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