from django.urls import path, include
from .views import mainActivityAlcantarillado

urlpatterns = [
    path('', mainActivityAlcantarillado, name='activity_alcantarillado'),
]
