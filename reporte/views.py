from __future__ import annotations

import json

from django.http import HttpResponse, HttpResponseBadRequest, HttpResponseRedirect
from django.shortcuts import get_object_or_404, render, redirect
from django.urls import reverse
from django.utils.timezone import localdate

from project.models import Project
from .models import ReportTemplate
from .utils_excel import (
    excel_libro_mayor,
    excel_actividades_detalle,
    excel_actividades_por_estado,
    excel_actividades_por_fecha,
)

# ---------------------------------------------------------------------
# HUB / CONSTRUCTOR / PLANTILLAS
# ---------------------------------------------------------------------

def report_hub(request, project_id: int):
    """
    Hub de reportes:
      - Reportes rápidos (4 establecidos) con vista previa/descarga.
      - Constructor (custom) con vista previa y guardado como plantilla.
      - Listado/carga/eliminación de plantillas guardadas por usuario.
    """
    project = get_object_or_404(Project, pk=project_id)
    today = localdate().isoformat()

    # Plantillas visibles: del usuario autenticado (si lo hay)
    if request.user.is_authenticated:
        templates_qs = ReportTemplate.objects.filter(project=project, owner=request.user)
    else:
        # Si no hay usuario, muestra las plantillas sin dueño (opcional)
        templates_qs = ReportTemplate.objects.filter(project=project, owner__isnull=True)

    # Cargar una plantilla guardada (?tpl=<id>)
    loaded_tpl_dict = None
    tpl_id = request.GET.get("tpl")
    if tpl_id:
        if request.user.is_authenticated:
            tpl = get_object_or_404(
                ReportTemplate, pk=tpl_id, project=project, owner=request.user
            )
        else:
            tpl = get_object_or_404(
                ReportTemplate, pk=tpl_id, project=project, owner__isnull=True
            )
        # Normalizamos a un dict para que el template lo consuma fácil
        payload = tpl.payload or {}
        loaded_tpl_dict = {
            "columns": payload.get("columns", []),
            "filters": payload.get("filters", {}),
            "order": payload.get("order", ""),
            "group_by": payload.get("group_by", ""),
            "name": tpl.name,
        }

    # Flags de vista previa para los reportes rápidos (UI)
    preview = request.GET.get("preview")
    context = {
        "project": project,
        "today": today,
        "templates": templates_qs,
        "loaded_tpl": loaded_tpl_dict,  # dict o None
    }
    if preview == "libro":
        context["preview_kind"] = "libro"
        context["preview_hint"] = "Vista previa del Libro mayor."
    elif preview == "detalle":
        context["preview_kind"] = "detalle"
        context["preview_hint"] = "Vista previa de Actividades (detalle)."
    elif preview == "estado":
        context["preview_kind"] = "estado"
        context["estado_val"] = request.GET.get("v", "E")
        context["preview_hint"] = f"Vista previa por estado ({context['estado_val']})."
    elif preview == "fecha":
        context["preview_kind"] = "fecha"
        context["fecha_val"] = request.GET.get("fecha", today)
        context["tipo_val"] = request.GET.get("tipo", "fin")
        context["preview_hint"] = f"Vista previa por fecha {context['tipo_val']} = {context['fecha_val']}."

    return render(request, "reporte/report_hub.html", context)


# ---------------------------------------------------------------------
# DESCARGAS (4 reportes establecidos)  -> Devuelven bytes de utils_excel
# ---------------------------------------------------------------------

def _xlsx_response(xbytes: bytes, filename: str) -> HttpResponse:
    resp = HttpResponse(
        xbytes,
        content_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
    )
    resp["Content-Disposition"] = f'attachment; filename="{filename}"'
    return resp


def excel_libro_mayor_view(request, project_id: int) -> HttpResponse:
    project = get_object_or_404(Project, pk=project_id)
    x = excel_libro_mayor(project)
    return _xlsx_response(x, "libro_mayor.xlsx")


def excel_actividades_detalle_view(request, project_id: int) -> HttpResponse:
    project = get_object_or_404(Project, pk=project_id)
    x = excel_actividades_detalle(project)
    return _xlsx_response(x, "actividades_detalle.xlsx")


def excel_por_estado_view(request, project_id: int) -> HttpResponse:
    project = get_object_or_404(Project, pk=project_id)
    estado = request.GET.get("estado", "E")
    x = excel_actividades_por_estado(project, estado)
    return xlsx_response(x, f"actividades_estado{estado}.xlsx")


def excel_actividades_por_fecha_view(request, project_id: int) -> HttpResponse:
    project = get_object_or_404(Project, pk=project_id)
    fecha = request.GET.get("fecha")
    tipo = request.GET.get("tipo", "fin")  # 'inicio' o 'fin'
    if not fecha:
        return HttpResponseBadRequest("Falta ?fecha=YYYY-MM-DD")
    x = excel_actividades_por_fecha(project, fecha, tipo)
    return xlsx_response(x, f"actividades_por{tipo}_{fecha}.xlsx")


# ---------------------------------------------------------------------
# PLANTILLAS (guardar / eliminar)
# ---------------------------------------------------------------------

def report_template_save(request, project_id: int):
    """
    Guarda o sobrescribe una plantilla (por nombre) para el usuario.
    Espera POST con:
      - name: str
      - payload: JSON (columns, filters, order, group_by)
    """
    if request.method != "POST":
        return HttpResponseBadRequest("Método no permitido")

    project = get_object_or_404(Project, pk=project_id)

    name = (request.POST.get("name") or "").strip()
    raw_payload = request.POST.get("payload") or "{}"

    if not name:
        return HttpResponseBadRequest("Nombre inválido")

    # Parseamos el JSON del payload de forma segura
    try:
        payload = json.loads(raw_payload)
        if not isinstance(payload, dict):
            payload = {}
    except Exception:
        payload = {}

    # Propietario (puede ser None si no hay auth)
    owner = request.user if request.user.is_authenticated else None

    # upsert por (project, owner, name)
    obj, _created = ReportTemplate.objects.update_or_create(
        project=project,
        owner=owner,
        name=name,
        defaults={"payload": payload},
    )

    # Redirige al hub con la plantilla cargada (namespaced)
    return HttpResponseRedirect(
        reverse("reporte:report_hub", kwargs={"project_id": project.id}) + f"?tpl={obj.id}"
    )


def report_template_delete(request, project_id: int, pk: int):
    """
    Elimina una plantilla del usuario actual (o sin dueño si no hay auth).
    """
    project = get_object_or_404(Project, pk=project_id)

    if request.user.is_authenticated:
        tpl = get_object_or_404(ReportTemplate, pk=pk, project=project, owner=request.user)
    else:
        tpl = get_object_or_404(ReportTemplate, pk=pk, project=project, owner__isnull=True)

    tpl.delete()
    return redirect(reverse("reporte:report_hub", kwargs={"project_id": project.id}))


# ---------------------------------------------------------------------
# ALIAS con los nombres que usaste en tus urls de exportación actuales
# ---------------------------------------------------------------------
excel_libro_mayor = excel_libro_mayor_view
excel_actividades_detalle = excel_actividades_detalle_view
excel_por_estado = excel_por_estado_view
excel_actividades_por_fecha = excel_actividades_por_fecha_view