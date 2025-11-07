from django.urls import path
from .views import demo_pdf, catalogo_pdf, libromayor_pdf, activities_pdf, fecha_pdf, demo_excel

urlpatterns = [
    path("demo/pdf/", demo_pdf, name="demo_pdf"),
    path("catalog/pdf/", catalogo_pdf, name="catalogo_pdf"),
    path("libromayor/pdf/", libromayor_pdf, name="libromayor_pdf"),
    path("actividades/pdf/", activities_pdf, name="activities_pdf"),
    path("fecha/pdf/", fecha_pdf, name="fecha_pdf"),
    path("demo/excel/", demo_excel, name="demo_excel"),
]
