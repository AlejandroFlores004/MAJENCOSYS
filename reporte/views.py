from django.http import HttpResponse
from django.template.loader import render_to_string
from django.shortcuts import render, get_object_or_404
from django.utils.timezone import now, localdate
from datetime import datetime
from weasyprint import HTML
from io import BytesIO
from openpyxl import Workbook
import json
from datetime import date, datetime
from decimal import Decimal

from django.http import HttpResponse, HttpResponseBadRequest, JsonResponse
from django.shortcuts import get_object_or_404, render, redirect
from django.utils import timezone
from django.views.decorators.http import require_http_methods

from project.models import Project
from catalog.models import Material, ManoObra, Herramienta, Equipo, Riesgo, Calidad, Ambiental, Hidrologica
from activity.models import Activity, Header
from schedule.models import Schedule
from django.db.models import Prefetch, Q

def report_center_pdf(request, pk: int):
    project = get_object_or_404(Project, pk=pk)

    context = {
        'project': project,
    }

    return render(request, 'report_center_pdf.html', context)

def demo_pdf(request, pk):
    project = get_object_or_404(Project, pk=pk)
    # Para Materiales ---------------------------------------------------
    
    qm = (Material.objects
          .filter(project=project)
          .select_related('unit')
          .order_by('name'))
    
    # Renderizar HTML con la lista de materiales
    html_string = render_to_string(
        'demo_pdf.html',
        {
            'nombre': 'ian',
            'apellido': 'adonay',
            'project': project,
            'materiales': qm,  # <-- aquí mandas la lista al HTML
        }
    )
    # base_url para que resuelva /static/ cuando lo uses
    pdf_bytes = HTML(string=html_string, base_url=request.build_absolute_uri('/')).write_pdf()
    return _pdf_response(pdf_bytes, filename="demo_weasyprint.pdf")

def catalogo_pdf(request, pk):
    project = get_object_or_404(Project, pk=pk)
    
    qm = (Material.objects
          .filter(project=project)
          .select_related('unit')
          .order_by('name'))
    
    qmo = (ManoObra.objects
          .filter(project=project)
          .order_by('name'))
    
    qhrr = (Herramienta.objects
          .filter(project=project)
          .order_by('name'))
    
    qeqp = (Equipo.objects
          .filter(project=project)
          .order_by('name'))
    
    qrsg = (Riesgo.objects
          .filter(project=project)
          .order_by('name'))
    
    qcld = (Calidad.objects
          .filter(project=project)
          .order_by('name'))
    
    qmbt = (Ambiental.objects
          .filter(project=project)
          .order_by('name'))
    
    qhdg = (Hidrologica.objects
          .filter(project=project)
          .order_by('name'))
    
    # Renderizar HTML con la lista
    html_string = render_to_string(
        'catalogo_pdf.html',
        {
            'project': project,
            'materiales': qm,
            'manoobra': qmo,
            'herramienta': qhrr,
            'equipo': qeqp,
            'riesgo': qrsg,
            'calidad': qcld,
            'ambiental': qmbt,
            'hidrologica': qhdg,
        }
    )

    pdf_bytes = HTML(string=html_string, base_url=request.build_absolute_uri('/')).write_pdf()
    return _pdf_response(pdf_bytes, filename="Reporte de Catalogo.pdf")

def libromayor_pdf(request, pk):
    project = get_object_or_404(Project, pk=pk)
    activity = Activity.objects.filter(project=project)

    activity_m = (Activity.objects.filter(project=project).prefetch_related('memoryMaterial_activity__material__unit').order_by('name'))
    activity_mo = (Activity.objects.filter(project=project).prefetch_related('MemoryManoObra_activity__manoobra'))
    activity_hrr = (Activity.objects.filter(project=project).prefetch_related('MemoryHerramienta_activity__herramienta'))
    activity_eqp = (Activity.objects.filter(project=project).prefetch_related('MemoryEquipo_activity__equipo'))
    activity_rsg = (Activity.objects.filter(project=project).prefetch_related('memoryRiesgos_activity__riesgo'))
    activity_cld = (Activity.objects.filter(project=project).prefetch_related('memoryCalidad_activity__calidad'))
    activity_mbt = (Activity.objects.filter(project=project).prefetch_related('memoryAmbiental_activity__ambiental'))
    activity_hdg = (Activity.objects.filter(project=project).prefetch_related('memoryHidrologica_activity__hidrologica'))

    with_materials = []
    with_manoonta = []
    with_herramienta = []
    with_equipo = []
    with_riesgo = []
    with_calidad = []
    with_ambiental = []
    with_hidrologica = []

    total_m = 0
    total_mo = 0
    total_hrr = 0
    total_eqp = 0
    total_rsg = 0
    total_cld = 0
    total_mbt = 0
    total_hdg = 0

    for am in activity_m:
        if am.memoryMaterial_activity.exists():
            with_materials.append(am)
        for elmt1 in am.memoryMaterial_activity.all():
            total_m += elmt1.material.price * elmt1.quantity

    for amo in activity_mo:
        if amo.MemoryManoObra_activity.exists():
            with_manoonta.append(amo)
        for elmt2 in amo.MemoryManoObra_activity.all():
            total_mo += (elmt2.manoobra.jornada / (1 - elmt2.prestaciones)) / elmt2.rendimiento

    for ahrr in activity_hrr:
        if ahrr.MemoryHerramienta_activity.exists():
            with_herramienta.append(ahrr)
        for elmt3 in ahrr.MemoryHerramienta_activity.all():
            total_hrr += elmt3.herramienta.costodia * elmt3.rendimiento

    for aeqp in activity_eqp:
        if aeqp.MemoryEquipo_activity.exists():
            with_equipo.append(aeqp)
        for elmt4 in aeqp.MemoryEquipo_activity.all():
            total_eqp += elmt4.equipo.costodia * elmt4.rendimiento

    for arsg in activity_rsg:
        if arsg.memoryRiesgos_activity.exists():
            with_riesgo.append(arsg)
        for elmt5 in arsg.memoryRiesgos_activity.all():
            total_rsg += elmt5.costo

    for acld in activity_cld:
        if acld.memoryCalidad_activity.exists():
            with_calidad.append(acld)
        for elmt6 in acld.memoryCalidad_activity.all():
            total_cld += elmt6.cantidad * elmt6.calidad.precio

    for ambt in activity_mbt:
        if ambt.memoryAmbiental_activity.exists():
            with_ambiental.append(ambt)
        for elmt7 in ambt.memoryAmbiental_activity.all():
            total_mbt += elmt7.valor

    for ahdg in activity_hdg:
        if ahdg.memoryHidrologica_activity.exists():
            with_hidrologica.append(ahdg)
        for elmt8 in ahdg.memoryHidrologica_activity.all():
            total_hdg += elmt8.costo

    # Renderizar HTML con la lista
    html_string2 = render_to_string(
        'libromayor_pdf.html',
        {
            'project':project,
            'activity':activity,
            'activity_m': activity_m,
            'with_materials': with_materials,
            'total_m': total_m,
            'activity_mo': activity_mo,
            'with_manoonta': with_manoonta,
            'total_mo': total_mo,
            'activity_hrr': activity_hrr,
            'with_herramienta': with_herramienta,
            'total_hrr': total_hrr,
            'activity_eqp': activity_eqp,
            'with_equipo': with_equipo,
            'total_eqp': total_eqp,
            'activity_rsg': activity_rsg,
            'with_riesgo': with_riesgo,
            'total_rsg': total_rsg,
            'activity_cld': activity_cld,
            'with_calidad': with_calidad,
            'total_cld': total_cld,
            'activity_mbt': activity_mbt,
            'with_ambiental': with_ambiental,
            'total_mbt': total_mbt,
            'activity_hdg': activity_hdg,
            'with_hidrologica': with_hidrologica,
            'total_hdg': total_hdg,
        }
    )

    pdf_bytes = HTML(string=html_string2, base_url=request.build_absolute_uri('/')).write_pdf()
    return _pdf_response(pdf_bytes, filename="Reporte de Libro Mayor.pdf")

def activities_pdf(request, pk):
    project = get_object_or_404(Project, pk=pk)

    activities_qs = (
        Activity.objects
        .filter(project=project)
        .prefetch_related(
            Prefetch("header_activity", queryset=Header.objects.all()),
            # Traemos el cronograma (uno por actividad según tu UniqueConstraint)
            Prefetch("schedule_activity", queryset=Schedule.objects.all())
        )
        .order_by("name")
    )

    # ---------------------------------------------------
    
    # Renderizar HTML con la lista de Actividades
    html_string = render_to_string(
        'activities_pdf.html',
        {
            'project': project,
            'activities': activities_qs,  # <-- aquí mandas la lista al HTML
        }
    )
    # base_url para que resuelva /static/ cuando lo uses
    pdf_bytes = HTML(string=html_string, base_url=request.build_absolute_uri('/')).write_pdf()
    return _pdf_response(pdf_bytes, filename="Reporte de Actividades.pdf")

def fecha_pdf(request, pk):
    project = get_object_or_404(Project, pk=pk)

    fecha_str = request.GET.get("fecha")
    if fecha_str:
        try:
            fecha_consulta = datetime.strptime(fecha_str, "%Y-%m-%d").date()
        except ValueError:
            fecha_consulta = now().date()  # valor por defecto si hay error
    else:
        fecha_consulta = now().date()


    activities_qs = (
        Activity.objects
        .filter(project=project,
            schedule_activity__start_date__lte=fecha_consulta,
            schedule_activity__end_date__gte=fecha_consulta
        )
        .prefetch_related(
            Prefetch("header_activity", queryset=Header.objects.all()),
            Prefetch("schedule_activity", queryset=Schedule.objects.all())
        )
        .order_by("name")
    )

    # ---------------------------------------------------
    
    # Renderizar HTML con la lista de Actividades
    html_string = render_to_string(
        'fecha_pdf.html',
        {
            'project': project,
            'activities': activities_qs,  # <-- aquí mandas la lista al HTML
            'fecha_consulta': fecha_consulta,
        }
    )
    # base_url para que resuelva /static/ cuando lo uses
    pdf_bytes = HTML(string=html_string, base_url=request.build_absolute_uri('/')).write_pdf()
    return _pdf_response(pdf_bytes, filename="Reporte del.pdf")

def _pdf_response(pdf_bytes: bytes, filename: str):
    resp = HttpResponse(pdf_bytes, content_type='application/pdf')
    resp['Content-Disposition'] = f'inline; filename="{filename}"'
    return resp

def demo_excel(request, pk):
    wb = Workbook()
    ws = wb.active
    ws.title = "Datos"
    ws.append(["ID", "Nombre", "Valor"])
    ws.append([1, "Fila 1", 123.45])
    ws.append([2, "Fila 2", 678.90])

    buf = BytesIO()
    wb.save(buf)
    buf.seek(0)

    resp = HttpResponse(
        buf.getvalue(),
        content_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
    )
    resp['Content-Disposition'] = 'attachment; filename="demo.xlsx"'
    return resp

from .models import ReportTemplate
from .excel_builders import (
    build_custom_report,
    excel_from_payload,
    excel_libro_mayor,
    excel_actividades_detalle,
    excel_actividades_por_fecha,
)

# ------------------ helpers ------------------


def _get_project(request, project_id=None):
    if project_id is None and request.resolver_match:
        kw = request.resolver_match.kwargs
        # Busca con distintos nombres
        project_id = kw.get("project_id") or kw.get("pk") or kw.get("id")

    if project_id is None:
        project_id = request.GET.get("project_id") or request.POST.get("project_id")

    if project_id is None:
        raise ValueError("project_id no está presente en la URL.")

    return get_object_or_404(Project, id=project_id)


def _format_cell(v):
    """
    Formateo SOLO para la vista previa en HTML (no afecta al Excel):
    - Fechas -> dd/mm/aaaa
    - Decimales -> 1,234.56
    """
    if isinstance(v, (date, datetime)):
        return v.strftime("%d/%m/%Y")
    if isinstance(v, Decimal):
        return f"{v:,.2f}"
    return v


# ------------------ hub ------------------


def report_hub(request, project_id=None, *args, **kwargs):
    project = _get_project(request, project_id)
    templates = ReportTemplate.objects.filter(project=project).order_by("-updated_at")

    loaded_tpl = None
    tpl_id = request.GET.get("tpl")
    if tpl_id:
        loaded_tpl = get_object_or_404(ReportTemplate, id=tpl_id, project=project)

    # --- Vista previa rápida (?preview=...) ---
    quick_preview_html = None
    pv = request.GET.get("preview")
    if pv in {"libro", "detalle", "estado", "fecha"}:
        if pv == "libro":
            payload = {
                "name": "Libro mayor",
                "columns": ["actividad", "estado", "inicio", "fin", "duracion", "total"],
                "order": "actividad",
            }
        elif pv == "detalle":
            payload = {
                "name": "Actividades detalle",
                "columns": ["actividad", "estado", "inicio", "fin", "duracion", "total"],
                "order": "inicio",
            }
        elif pv == "estado":
            v = (request.GET.get("v") or "E").upper()
            if v not in ("P", "E", "F"):
                v = "E"
            payload = {
                "name": f"Actividades estado {v}",
                "columns": ["actividad", "estado", "inicio", "fin", "duracion", "total"],
                "filters": {"estado": [v]},
                "order": "actividad",
            }
        else:  # pv == "fecha"
            fecha = request.GET.get("fecha") or timezone.now().date().isoformat()
            tipo = (request.GET.get("tipo") or "fin").lower()
            if tipo not in ("inicio", "fin"):
                tipo = "fin"
            if tipo == "inicio":
                filters = {"ini_desde": fecha, "ini_hasta": fecha}
            else:
                filters = {"fin_desde": fecha, "fin_hasta": fecha}
            payload = {
                "name": f"Actividades por fecha {tipo} {fecha}",
                "columns": ["actividad", "estado", "inicio", "fin", "duracion", "total"],
                "filters": filters,
                "order": tipo,
            }

        headers, rows = build_custom_report(project, payload)
        page = int(request.GET.get("page", 1))
        size = int(request.GET.get("page_size", 10))
        total = len(rows)
        start = (page - 1) * size
        end = start + size
        rows_page = rows[start:end]

        # Formato amigable sólo para HTML
        rows_display = [[_format_cell(c) for c in row] for row in rows_page]

        quick_preview_html = render(
            request,
            "reporte/includes/_preview_table.html",
            {
                "headers": headers,
                "rows": rows_display,
                "groups": None,
                "page": page,
                "has_prev": page > 1,
                "has_next": end < total,
                "total_count": total,
            },
        ).content.decode("utf-8")

    ctx = {
        "project": project,
        "templates": templates,
        "loaded_tpl": loaded_tpl,
        "today": timezone.now().date().isoformat(),
        "quick_preview_html": quick_preview_html,
    }
    return render(request, "reporte/report_hub.html", ctx)


# ------------------ vista previa desde constructor ------------------


@require_http_methods(["POST"])
def preview_custom(request, project_id=None, *args, **kwargs):
    project = get_object_or_404(Project, pk=project_id)
    payload = json.loads(request.body.decode("utf-8") or "{}")
    headers, rows = build_custom_report(project, payload)

    page = int(request.GET.get("page", 1))
    size = int(request.GET.get("page_size", 10))
    total = len(rows)
    start = (page - 1) * size
    end = start + size
    rows_page = rows[start:end]

    rows_display = [[_format_cell(c) for c in row] for row in rows_page]

    return render(
        request,
        "reporte/includes/_preview_table.html",
        {
            "headers": headers,
            "rows": rows_display,
            "groups": None,
            "page": page,
            "has_prev": page > 1,
            "has_next": end < total,
            "total_count": total,
        },
    )


@require_http_methods(["POST"])
def preview_template(request, pk, project_id=None, *args, **kwargs):
    project = get_object_or_404(Project, pk=project_id)
    tpl = get_object_or_404(ReportTemplate, pk=pk, project=project)
    payload = tpl.payload or {}
    headers, rows = build_custom_report(project, payload)

    page = int(request.GET.get("page", 1))
    size = int(request.GET.get("page_size", 10))
    total = len(rows)
    start = (page - 1) * size
    end = start + size
    rows_page = rows[start:end]

    rows_display = [[_format_cell(c) for c in row] for row in rows_page]

    return render(
        request,
        "reporte/includes/_preview_table.html",
        {
            "headers": headers,
            "rows": rows_display,
            "groups": None,
            "page": page,
            "has_prev": page > 1,
            "has_next": end < total,
            "total_count": total,
            "template": tpl,
        },
    )


# ------------------ descargar excel desde constructor ------------------


@require_http_methods(["POST"])
def excel_custom(request, project_id):
    project = get_object_or_404(Project, pk=project_id)
    payload = json.loads(request.body.decode("utf-8") or "{}")

    # Usamos el motor completo de excel_builders (con estilos, totales y auto-width)
    x = excel_from_payload(project, payload)

    resp = HttpResponse(
        x,
        content_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
    )
    resp["Content-Disposition"] = (
        f'attachment; filename="reporte_custom_{project.id}.xlsx"'
    )
    return resp


# ------------------ rápidos (compat) ------------------


def excel_libro_mayor_view(request, project_id=None, *args, **kwargs):
    project = _get_project(request, project_id)
    x = excel_libro_mayor(project)
    resp = HttpResponse(
        x,
        content_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
    )
    resp["Content-Disposition"] = f'attachment; filename="libro_mayor_{project.id}.xlsx"'
    return resp


def excel_actividades_detalle_view(request, project_id=None, *args, **kwargs):
    project = _get_project(request, project_id)
    x = excel_actividades_detalle(project)
    resp = HttpResponse(
        x,
        content_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
    )
    resp["Content-Disposition"] = f'attachment; filename="actividades_{project.id}.xlsx"'
    return resp


def excel_por_estado_view(request, project_id=None, *args, **kwargs):
    project = _get_project(request, project_id)
    estado = request.GET.get("estado") or "E"
    payload = {
        "name": f"Actividades estado {estado}",
        "columns": ["actividad", "estado", "inicio", "fin", "duracion", "total"],
        "filters": {"estado": [estado]},
        "order": "actividad",
    }
    x = excel_from_payload(project, payload)
    resp = HttpResponse(
        x,
        content_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
    )
    resp["Content-Disposition"] = (
        f'attachment; filename="por_estado_{estado}_{project.id}.xlsx"'
    )
    return resp


def excel_actividades_por_fecha_view(request, project_id=None, *args, **kwargs):
    project = _get_project(request, project_id)
    fecha = request.GET.get("fecha")
    tipo = request.GET.get("tipo", "fin")
    if not fecha:
        return HttpResponseBadRequest("Falta ?fecha=YYYY-MM-DD")
    x = excel_actividades_por_fecha(project, fecha, tipo)
    resp = HttpResponse(
        x,
        content_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
    )
    resp["Content-Disposition"] = (
        f'attachment; filename="por_fecha_{tipo}_{fecha}_{project.id}.xlsx"'
    )
    return resp


# ------------------ plantillas (guardar / borrar / descargar) ------------------


@require_http_methods(["POST"])
def report_template_save(request, project_id):
    project = get_object_or_404(Project, pk=project_id)
    try:
        payload = json.loads(request.POST.get("payload") or "{}")
    except json.JSONDecodeError:
        return HttpResponseBadRequest("Payload inválido")

    name = (request.POST.get("name") or "").strip()
    if not name:
        return HttpResponseBadRequest("Debes ingresar un nombre para el reporte.")

    tpl, _created = ReportTemplate.objects.get_or_create(
        project=project,
        name=name,
        defaults={"owner": request.user},
    )
    tpl.payload = payload
    tpl.owner = tpl.owner or request.user
    tpl.save(update_fields=["payload", "owner", "updated_at"])
    return redirect("reporte:report_hub", project_id=project.id)


def report_template_delete(request, pk, project_id=None, *args, **kwargs):
    project = _get_project(request, project_id)
    get_object_or_404(ReportTemplate, id=pk, project=project).delete()
    return redirect("reporte:report_hub", project_id=project.id)


def excel_from_template(request, pk, project_id=None, *args, **kwargs):
    project = _get_project(request, project_id)
    tpl = get_object_or_404(ReportTemplate, id=pk, project=project)

    payload = tpl.payload
    if isinstance(payload, str):
        try:
            payload = json.loads(payload)
        except Exception:
            return HttpResponseBadRequest("Payload de plantilla inválido")

    x = excel_from_payload(project, payload)
    resp = HttpResponse(
        x,
        content_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
    )
    filename = (tpl.name or "reporte").replace('"', "").replace("'", "")
    resp["Content-Disposition"] = f'attachment; filename="{filename}_{project.id}.xlsx"'
    return resp


@require_http_methods(["GET"])
def template_load(request, project_id, tpl_id):
    project = get_object_or_404(Project, pk=project_id)
    tpl = get_object_or_404(ReportTemplate, pk=tpl_id, project=project)
    return JsonResponse(
        {
            "ok": True,
            "id": tpl.id,
            "name": tpl.name,
            "payload": tpl.payload or {},
        }
    )


@require_http_methods(["POST"])
def template_refresh(request, project_id, tpl_id):
    """
    Recalcula la plantilla para asegurarse de que el payload es válido
    y simplemente actualiza `updated_at`. Si algo truena, devuelve 400.
    """
    project = get_object_or_404(Project, pk=project_id)
    tpl = get_object_or_404(ReportTemplate, pk=tpl_id, project=project)

    try:
        build_custom_report(project, tpl.payload or {})
    except Exception:
        return JsonResponse({"ok": False}, status=400)

    tpl.save(update_fields=["updated_at"])
    return JsonResponse({"ok": True})


@require_http_methods(["POST"])
def template_update(request, project_id, tpl_id):
    project = get_object_or_404(Project, pk=project_id)
    tpl = get_object_or_404(ReportTemplate, pk=tpl_id, project=project)

    try:
        data = json.loads(request.body.decode("utf-8") or "{}")
    except Exception:
        return HttpResponseBadRequest("JSON inválido")

    name = (data.get("name") or "").strip()
    if not name:
        return HttpResponseBadRequest("Debes ingresar un nombre.")

    tpl.name = name
    if "payload" in data:
        tpl.payload = data["payload"]
    tpl.save(update_fields=["name", "payload", "updated_at"])
    return JsonResponse({"ok": True, "id": tpl.id})


@require_http_methods(["POST"])
def template_delete(request, project_id, tpl_id):
    project = get_object_or_404(Project, pk=project_id)
    tpl = get_object_or_404(ReportTemplate, pk=tpl_id, project=project)
    tpl.delete()
    return JsonResponse({"ok": True})
