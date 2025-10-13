from django.urls import path, include
from .views import mainActivy, crearActivity
urlpatterns = [
    path('',mainActivy,name='mainAcivity'),
    path('crear/actividad/',crearActivity, name='crearActivity')
]
