from django.urls import path
from .views import(
    projectMain,           # LISTADO
    projectDetail,         # Detalle individual
    projectCreate,         # Crear
    projectUpdate,         # Editar
    projectDelete,         # Eliminar (confirmación)
    projectDetailList,     # Página del botón "Detalles"
    project_file_list_create,
    project_file_download,
    project_file_delete
)

urlpatterns = [
    path('',                    projectMain,        name='projectMain'),
    path('detalles/',           projectDetailList,  name='projectDetailList'),
    path('nuevo/',              projectCreate,      name='projectCreate'),
    path('<int:pk>/',           projectDetail,      name='projectDetail'),
    path('<int:pk>/editar/',    projectUpdate,      name='projectUpdate'),
    path('<int:pk>/eliminar/',  projectDelete,      name='projectDelete'),
   path('<int:pk>/archivos/', project_file_list_create, name='projectFiles'),
    path('<int:pk>/archivos/<int:file_id>/descargar/', project_file_download, name='projectFileDownload'),
     path('<int:pk>/archivos/<int:file_id>/eliminar/', project_file_delete, name='projectFileDelete'),
]
