from io import BytesIO
from openpyxl import Workbook
from django.db.models import F, Sum
from django.db.models.functions import Coalesce

from activity.models import Activity, MemoryMaterial, MemoryManoObra, MemoryHerramienta, MemoryEquipo, \
    MemoryRiesgos, MemoryCalidad, MemoryAmbiental, MemoryHidrologica
from schedule.models import schedule as Schedule

# ---- costos por actividad -------------------------------------------------

def _totales_costos(activity_ids):
    def agg(qs): return {x["activity_id"]: x["total"] for x in qs}

    mat = (MemoryMaterial.objects.filter(activity_id__in=activity_ids)
           .annotate(sub=F("quantity") * F("material__price"))
           .values("activity_id").annotate(total=Coalesce(Sum("sub"), 0)))
    mo  = (MemoryManoObra.objects.filter(activity_id__in=activity_ids)
           .annotate(sub=F("manoobra__jornada") * (1+F("prestaciones")) * F("rendimiento"))
           .values("activity_id").annotate(total=Coalesce(Sum("sub"), 0)))
    hrr = (MemoryHerramienta.objects.filter(activity_id__in=activity_ids)
           .annotate(sub=F("herramienta__costodia") * F("rendimiento"))
           .values("activity_id").annotate(total=Coalesce(Sum("sub"), 0)))
    eqp = (MemoryEquipo.objects.filter(activity_id__in=activity_ids)
           .annotate(sub=F("equipo__costodia") * F("rendimiento"))
           .values("activity_id").annotate(total=Coalesce(Sum("sub"), 0)))
    rsg = (MemoryRiesgos.objects.filter(activity_id__in=activity_ids)
           .values("activity_id").annotate(total=Coalesce(Sum("costo"), 0)))
    cld = (MemoryCalidad.objects.filter(activity_id__in=activity_ids)
           .annotate(sub=F("calidad__precio") * F("cantidad"))
           .values("activity_id").annotate(total=Coalesce(Sum("sub"), 0)))
    amb = (MemoryAmbiental.objects.filter(activity_id__in=activity_ids)
           .values("activity_id").annotate(total=Coalesce(Sum("valor"), 0)))
    hdg = (MemoryHidrologica.objects.filter(activity_id__in=activity_ids)
           .values("activity_id").annotate(total=Coalesce(Sum("costo"), 0)))

    res = {}
    for m in [agg(mat), agg(mo), agg(hrr), agg(eqp), agg(rsg), agg(cld), agg(amb), agg(hdg)]:
        for k, v in m.items():
            res[k] = res.get(k, 0) + float(v)
    return res

# ---- helper para crear archivo -------------------------------------------

def _wb_bytes(wb: Workbook) -> bytes:
    buf = BytesIO()
    wb.save(buf)
    buf.seek(0)
    return buf.getvalue()

# ---- 1) Libro mayor -------------------------------------------------------

def excel_libro_mayor(project):
    wb = Workbook()
    ws = wb.active
    ws.title = "Libro mayor"

    qs = Activity.objects.filter(project=project).order_by("name")
    ids = list(qs.values_list("id", flat=True))
    sch = {s.activity_id: s for s in Schedule.objects.filter(activity_id__in=ids)}
    tot = _totales_costos(ids)

    ws.append(["Actividad","Estado","Inicio","Fin","Total (USD)"])
    for a in qs:
        s = sch.get(a.id)
        ws.append([
            a.name,
            (s.get_status_display() if s else "Sin cronograma"),
            (s.start_date if s else None),
            (s.end_date if s else None),
            round(tot.get(a.id, 0), 2)
        ])

    return _wb_bytes(wb)

# ---- 2) Actividades detalle ----------------------------------------------

def excel_actividades_detalle(project):
    wb = Workbook()
    ws = wb.active
    ws.title = "Actividades"

    qs = (Activity.objects.filter(project=project)
          .prefetch_related("schedule_activity").order_by("name"))
    sch = {s.activity_id: s for s in Schedule.objects.filter(activity__project=project)}

    ws.append(["Actividad","Estado","Inicio","Fin","Duración (días)"])
    for a in qs:
        s = sch.get(a.id)
        dur = (s.end_date - s.start_date).days if s and s.end_date and s.start_date else None
        ws.append([a.name, (s.get_status_display() if s else "Sin cronograma"),
                   (s.start_date if s else None), (s.end_date if s else None), dur])

    return _wb_bytes(wb)

# ---- 3) Por estado --------------------------------------------------------

def excel_actividades_por_estado(project, estado):
    wb = Workbook()
    ws = wb.active
    ws.title = f"Estado {estado}"

    sch = (Schedule.objects.filter(activity__project=project, status=estado)
           .select_related("activity").order_by("activity__name"))

    ws.append(["Actividad","Estado","Inicio","Fin"])
    for s in sch:
        ws.append([s.activity.name, s.get_status_display(), s.start_date, s.end_date])

    return _wb_bytes(wb)

# ---- 4) Por fecha ---------------------------------------------------------

def excel_actividades_por_fecha(project, fecha, tipo="fin"):
    wb = Workbook()
    ws = wb.active
    ws.title = f"Por fecha {tipo}"

    filtro = {"activity__project": project, "end_date": fecha}
    if tipo == "inicio":
        filtro = {"activity__project": project, "start_date": fecha}

    sch = (Schedule.objects.filter(**filtro)
           .select_related("activity").order_by("activity__name"))

    ws.append(["Actividad","Estado","Fecha","Duración (días)"])
    for s in sch:
        dur = (s.end_date - s.start_date).days if s.end_date and s.start_date else None
        ws.append([s.activity.name, s.get_status_display(),
                   (s.start_date if tipo == "inicio" else s.end_date), dur])

    return _wb_bytes(wb)
