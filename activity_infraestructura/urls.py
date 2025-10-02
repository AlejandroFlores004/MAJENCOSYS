# urls.py
from django.urls import path
from .views import mainActivityInfraestructura, createActivityInfraestructura, updateActivityInfraestructura

urlpatterns = [
    path('', mainActivityInfraestructura, name='mainActivityInfraestructura'),
    path('nueva-actividad/', createActivityInfraestructura, name='create_new_activity_infraestructura'),
    path('actividad/<int:activity_id>/editar/', updateActivityInfraestructura, name='update_activity_infraestructura'),
]
