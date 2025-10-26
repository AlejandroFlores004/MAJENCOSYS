from django.urls import path
from .views import demo_pdf, demo_excel

urlpatterns = [
    path("demo/pdf/", demo_pdf, name="demo_pdf"),
    path("demo/excel/", demo_excel, name="demo_excel"),
]
