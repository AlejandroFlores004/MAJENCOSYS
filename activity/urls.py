from django.urls import path, include
from .views import mainActivy, crearActivity, editarActivity, detailActivityFinished, detailActivityPlanned, memoryManager, formMemoryMaterials, formMemoryManoObra, formMemoryHerramienta, formMemoryEquipo, formMemoryRiesgos, formMemoryCalidad, formMemoryAmbiental,formMemoryHidrologica
urlpatterns = [
    path('',mainActivy,name='mainAcivity'),
    path('crear/actividad/',crearActivity, name='crearActivity'),
    path('editar/actividad/<int:activity_id>/', editarActivity, name='editarActivity'),
    path('actividad_planeada/<int:activity_id>/', detailActivityPlanned, name='detailActivityPlanned'),
    path('actividad_finalizada/<int:activity_id>/', detailActivityFinished, name='detailActivityFinished'),
    path('manager/memorias/<int:activity_id>/', memoryManager, name='memoryMananer'),
    path('manager/memorias/<int:activity_id>/materiales', formMemoryMaterials, name='memoryMateriales'),
    path('manager/memorias/<int:activity_id>/mano_obra', formMemoryManoObra, name='memoryManoObra'),
    path('manager/memorias/<int:activity_id>/herramientas', formMemoryHerramienta, name='memoryHerramienta'),
    path('manager/memorias/<int:activity_id>/equipo', formMemoryEquipo, name='memoryEquipo'),
    path('manager/memorias/<int:activity_id>/riesgos', formMemoryRiesgos, name='memoryRiesgos'),
    path('manager/memorias/<int:activity_id>/control_calidad', formMemoryCalidad, name='memoryCalidad'),
    path('manager/memorias/<int:activity_id>/control_ambiental', formMemoryAmbiental, name='memoryAmbiental'),
    path('manager/memorias/<int:activity_id>/pruebas_hidrologicas', formMemoryHidrologica, name='memoryHidrologica'),
]
