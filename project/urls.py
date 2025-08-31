from django.contrib import admin
from django.urls import path,include
from .views import projectMain, projectDetail

urlpatterns = [
    path('', projectMain, name='projectMain'), # /project/ muestra la lista
    path("<int:pk>/", projectDetail, name="projectDetail"), #Detalle de proyecto
  #  path('/formulario_project', userFormView, name='projectForm'),
  
]