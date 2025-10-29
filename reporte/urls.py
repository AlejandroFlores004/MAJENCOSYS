from django.urls import path
from . import views

app_name = "reporte"  # ✅ importante para usar {% url 'reporte:...' %} en templates

urlpatterns = [
    # --- Vista principal del módulo de reportes ---
    path("", views.report_hub, name="report_hub"),  

    # --- Guardar y eliminar plantillas de reportes ---
    path("save/", views.report_template_save, name="report_template_save"),
    path("delete/<int:pk>/", views.report_template_delete, name="report_template_delete"),

    # --- Endpoints de exportación Excel ---
    path("excel/libro-mayor/", views.excel_libro_mayor_view, name="excel_libro_mayor"),
    path("excel/actividades/", views.excel_actividades_detalle_view, name="excel_actividades_detalle"),
    path("excel/por-fecha/", views.excel_actividades_por_fecha_view, name="excel_actividades_por_fecha"),
    path("excel/por-estado/", views.excel_por_estado_view, name="excel_por_estado"),
]
