from django.urls import path, include
from .views import mainActivityInfraestructura, createActivityInfraestructura

urlpatterns = [
    path('', mainActivityInfraestructura, name='mainActivityInfraestructura'),
    path('nueva_actividad', createActivityInfraestructura, name='create_new_activity_infraestructura'),
]