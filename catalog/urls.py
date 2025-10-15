from django.urls import path
from .views import MainCatalog, CreateMaterial, EditMaterial, CreateManoObra, EditManoObra, CreateHerramienta, EditHerramienta, CreateEquipo, EditEquipo, CreateRiesgo, EditRiesgo, CreateCalidad, EditCalidad, CreateAmbiental, EditAmbiental, CreateHidrologica, EditHidrologica

urlpatterns = [
    path('',MainCatalog,name='mainCatalog'),
    path('crear/material/',CreateMaterial, name='crearMaterial'),
    path('editar/material/<int:material_id>/', EditMaterial, name='editarMaterial'),
    path('crear/manoobra/',CreateManoObra, name='crearManoObra'),
    path('editar/manoobra/<int:manoobra_id>/', EditManoObra, name='editarManoObra'),
    path('crear/herramienta/',CreateHerramienta, name='crearHerramienta'),
    path('editar/herramienta/<int:herramienta_id>/', EditHerramienta, name='editarHerramienta'),
    path('crear/equipo/',CreateEquipo, name='crearEquipo'),
    path('editar/equipo/<int:equipo_id>/', EditEquipo, name='editarEquipo'),
    path('crear/riesgo/',CreateRiesgo, name='crearRiesgo'),
    path('editar/riesgo/<int:riesgo_id>/', EditRiesgo, name='editarRiesgo'),
    path('crear/calidad/',CreateCalidad, name='crearCalidad'),
    path('editar/calidad/<int:calidad_id>/', EditCalidad, name='editarCalidad'),
    path('crear/ambiental/',CreateAmbiental, name='crearAmbiental'),
    path('editar/ambiental/<int:ambiental_id>/', EditAmbiental, name='editarAmbiental'),
    path('crear/hidrologica/',CreateHidrologica, name='crearHidrologica'),
    path('editar/hidrologica/<int:hidrologica_id>/', EditHidrologica, name='editarHidrologica'),
]
