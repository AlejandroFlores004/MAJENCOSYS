from django.urls import path, include
from .views import mainActivy, crearActivity, editarActivity, memoryManager, formMemoryMaterials
urlpatterns = [
    path('',mainActivy,name='mainAcivity'),
    path('crear/actividad/',crearActivity, name='crearActivity'),
    path('editar/actividad/<int:activity_id>/', editarActivity, name='editarActivity'),
    path('manager/memorias/<int:activity_id>/', memoryManager, name='memoryMananer'),
    path('manager/memorias/<int:activity_id>/materiales', formMemoryMaterials, name='memoryMateriales')
]
