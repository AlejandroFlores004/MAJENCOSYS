from django.urls import path
from .views import MainCatalog, CreateMaterial, EditMaterial

urlpatterns = [
    path('',MainCatalog,name='mainCatalog'),
    path('crear/material/',CreateMaterial, name='crearMaterial'),
    path('editar/material/<int:material_id>/', EditMaterial, name='editarMaterial'),

]
