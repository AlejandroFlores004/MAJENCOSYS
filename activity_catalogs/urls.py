from django.urls import path
from .views import homeCatalogs, formTools, editTool, formLabour, editLabour, formMaterial, editMaterial

urlpatterns = [
    path('', homeCatalogs, name='activity_catalogs_home'),
    path('tools/', formTools, name='tools_list'),
    path('tools/edit/<int:tool_id>/', editTool, name='edit_tool'),
    path('mano_obra/', formLabour, name='labour_list'),
    path('mano_obra/edit/<int:labour_id>/', editLabour, name='edit_labour'),
    path('material/', formMaterial, name='material_list'),
    path('material/edit/<int:material_id>/', editMaterial, name='edit_material'),
]
