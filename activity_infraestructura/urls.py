from django.urls import path, include
from .views import mainActivityInfraestructura

urlpatterns = [
    path('', mainActivityInfraestructura, name='mainActivityInfraestructura'),
]