# reporte/urls.py
from django.urls import path
from . import views

app_name = "reporte"

urlpatterns = [
    # Hub principal de reportes del proyecto
    path("", views.report_hub, name="report_hub"),

    # Constructor: preview y excel
    path("preview/custom/", views.preview_custom, name="preview_custom"),
    path("excel/custom/", views.excel_custom, name="excel_custom"),

    # Plantillas: guardar desde el constructor
    path("save/", views.report_template_save, name="report_template_save"),

    # Plantillas: operaciones por id
    path("template/<int:pk>/load/", views.template_load, name="template_load"),
    path("template/<int:pk>/refresh/", views.template_refresh, name="template_refresh"),
    path("template/<int:pk>/update/", views.template_update, name="template_update"),
    path("template/<int:pk>/delete/", views.template_delete, name="template_delete"),

    # Vista previa de plantilla
    path(
        "template/<int:pk>/preview/",
        views.preview_template,
        name="preview_template",
    ),

    # Compat: borrar y descargar usando las vistas viejas
    path("delete/<int:pk>/", views.report_template_delete, name="report_template_delete"),
    path("excel/<int:pk>/", views.excel_from_template, name="excel_from_template"),

    # Reportes rápidos (excel directo)
    path("excel/libro-mayor/", views.excel_libro_mayor_view, name="excel_libro_mayor"),
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
