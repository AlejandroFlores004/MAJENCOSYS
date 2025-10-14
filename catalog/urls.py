from django.urls import path
from .views import MainCatalog, CreateMaterial, EditMaterial, CreateManoObra, EditManoObra, CreateHerramienta, EditHerramienta

urlpatterns = [
    path('',MainCatalog,name='mainCatalog'),
    path('crear/material/',CreateMaterial, name='crearMaterial'),
    path('editar/material/<int:material_id>/', EditMaterial, name='editarMaterial'),
    path('crear/manoobra/',CreateManoObra, name='crearManoObra'),
    path('editar/manoobra/<int:manoobra_id>/', EditManoObra, name='editarManoObra'),
    path('crear/herramienta/',CreateHerramienta, name='crearHerramienta'),
    path('editar/herramienta/<int:herramienta_id>/', EditHerramienta, name='editarHerramienta'),

]
