# project/urls.py
from django.contrib import admin                   # (no se usa aquí, pero puedes dejarlo)
from django.urls import path, include              # include no se usa en este archivo
from .views import (projectMain,projectDetail,projectCreate,projectUpdate,projectDelete,projectDetailList)

urlpatterns = [

    path("", projectMain, name="projectMain"),
    path("nuevo/", projectCreate, name="projectCreate"),
    path("<int:pk>/", projectDetail, name="projectDetail"),
    path("<int:pk>/editar/", projectUpdate, name="projectUpdate"),
    path("<int:pk>/eliminar/", projectDelete, name="projectDelete"),
    path('detalles/', projectDetailList, name='projectDetailList'),

]
