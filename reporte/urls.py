# reporte/urls.py
from django.urls import path
from . import views

urlpatterns = [
    # PDF / DEMOS CLÁSICOS
    path("", views.report_center_pdf, name="report_center_pdf"),
    path("demo/pdf/", views.demo_pdf, name="demo_pdf"),
    path("catalog/pdf/", views.catalogo_pdf, name="catalogo_pdf"),
    path("libromayor/pdf/", views.libromayor_pdf, name="libromayor_pdf"),
    path("actividades/pdf/", views.activities_pdf, name="activities_pdf"),
    path("fecha/pdf/", views.fecha_pdf, name="fecha_pdf"),
    path("demo/excel/", views.demo_excel, name="demo_excel"),

    # Hub principal de reportes del proyecto (el que ves en /reportes/excel/)
    path("excel/", views.report_hub, name="report_hub"),

    # Constructor: preview y excel
    path("preview/custom/", views.preview_custom, name="preview_custom"),
    path("excel/custom/", views.excel_custom, name="excel_custom"),

    # Plantillas: guardar desde el constructor
    path("save/", views.report_template_save, name="report_template_save"),

    # Plantillas: operaciones por id (OJO: ya no usamos pk, usamos tpl_id)
    path("template/<int:tpl_id>/load/", views.template_load, name="template_load"),
    path("template/<int:tpl_id>/refresh/", views.template_refresh, name="template_refresh"),
    path("template/<int:tpl_id>/update/", views.template_update, name="template_update"),
    path("template/<int:tpl_id>/delete/", views.template_delete, name="template_delete"),

    # Vista previa de plantilla
    path(
        "template/<int:tpl_id>/preview/",
        views.preview_template,
        name="preview_template",
    ),

    # Compat: borrar y descargar usando las vistas viejas
    path(
        "delete/<int:tpl_id>/",
        views.report_template_delete,
        name="report_template_delete",
    ),
    path(
        "excel/<int:tpl_id>/",
        views.excel_from_template,
        name="excel_from_template",
    ),

    # Reportes rápidos (excel directo)
    path(
        "excel/libro-mayor/",
        views.excel_libro_mayor_view,
        name="excel_libro_mayor",
    ),
    path(
        "excel/actividades/",
        views.excel_actividades_detalle_view,
        name="excel_actividades_detalle",
    ),
    path("excel/por-estado/", views.excel_por_estado_view, name="excel_por_estado"),
    path(
        "excel/por-fecha/",
        views.excel_actividades_por_fecha_view,
        name="excel_actividades_por_fecha",
    ),
]
