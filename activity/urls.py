from django.urls import path, include
from .views import mainActivy, crearActivity, editarActivity
urlpatterns = [
    path('',mainActivy,name='mainAcivity'),
    path('crear/actividad/',crearActivity, name='crearActivity'),
    path('editar/actividad/<int:activity_id>/', editarActivity, name='editarActivity')
]
