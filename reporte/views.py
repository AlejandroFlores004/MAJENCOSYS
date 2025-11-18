import json
from datetime import date, datetime
from decimal import Decimal

from django.http import HttpResponse, HttpResponseBadRequest, JsonResponse
from django.shortcuts import get_object_or_404, render, redirect
from django.utils import timezone
from django.views.decorators.http import require_http_methods

from project.models import Project
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
        project_id = request.resolver_match.kwargs.get("project_id")
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
def template_load(request, project_id, pk):
    project = get_object_or_404(Project, pk=project_id)
    tpl = get_object_or_404(ReportTemplate, pk=pk, project=project)
    return JsonResponse(
        {
            "ok": True,
            "id": tpl.id,
            "name": tpl.name,
            "payload": tpl.payload or {},
        }
    )


@require_http_methods(["POST"])
def template_refresh(request, project_id, pk):
    """
    Recalcula la plantilla para asegurarse de que el payload es válido
    y simplemente actualiza `updated_at`. Si algo truena, devuelve 400.
    """
    project = get_object_or_404(Project, pk=project_id)
    tpl = get_object_or_404(ReportTemplate, pk=pk, project=project)

    try:
        build_custom_report(project, tpl.payload or {})
    except Exception:
        return JsonResponse({"ok": False}, status=400)

    tpl.save(update_fields=["updated_at"])
    return JsonResponse({"ok": True})


@require_http_methods(["POST"])
def template_update(request, project_id, pk):
    project = get_object_or_404(Project, pk=project_id)
    tpl = get_object_or_404(ReportTemplate, pk=pk, project=project)

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
def template_delete(request, project_id, pk):
    project = get_object_or_404(Project, pk=project_id)
    tpl = get_object_or_404(ReportTemplate, pk=pk, project=project)
    tpl.delete()
    return JsonResponse({"ok": True})
