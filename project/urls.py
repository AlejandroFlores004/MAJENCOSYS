# project/urls.py
from django.urls import path
from .views import (
    projectMain, projectDetail, projectCreate,
    projectUpdate, projectDelete, projectDetailList
)

urlpatterns = [
    path("", projectMain, name="projectMain"),
    path("nuevo/", projectCreate, name="projectCreate"),
    path("<int:pk>/", projectDetail, name="projectDetail"),
    path("<int:pk>/editar/", projectUpdate, name="projectUpdate"),
    path("<int:pk>/eliminar/", projectDelete, name="projectDelete"),
    path("detalles/", projectDetailList, name="projectDetailList"),
]
