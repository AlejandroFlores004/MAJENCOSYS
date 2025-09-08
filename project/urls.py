from django.urls import path
from .views import (
    projectMain,           # LISTADO
    projectDetail,         # Detalle individual
    projectCreate,         # Crear
    projectUpdate,         # Editar
    projectDelete,         # Eliminar (confirmación)
    projectDetailList,     # Página del botón "Detalles"
)

urlpatterns = [
    path('',                    projectMain,        name='projectMain'),
    path('detalles/',           projectDetailList,  name='projectDetailList'),
    path('nuevo/',              projectCreate,      name='projectCreate'),
    path('<int:pk>/',           projectDetail,      name='projectDetail'),
    path('<int:pk>/editar/',    projectUpdate,      name='projectUpdate'),
    path('<int:pk>/eliminar/',  projectDelete,      name='projectDelete'),
]
