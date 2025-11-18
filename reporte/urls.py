# reporte/urls.py
from django.urls import path
from .views import report_center_pdf, demo_pdf, catalogo_pdf, libromayor_pdf, activities_pdf, fecha_pdf, demo_excel
from . import views

app_name = "reporte"

urlpatterns = [
    path("", report_center_pdf, name="report_center_pdf"),  
    path("demo/pdf/", demo_pdf, name="demo_pdf"),
    path("catalog/pdf/", catalogo_pdf, name="catalogo_pdf"),
    path("libromayor/pdf/", libromayor_pdf, name="libromayor_pdf"),
    path("actividades/pdf/", activities_pdf, name="activities_pdf"),
    path("fecha/pdf/", fecha_pdf, name="fecha_pdf"),
    path("demo/excel/", demo_excel, name="demo_excel"),
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
