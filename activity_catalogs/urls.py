from django.urls import path
from .views import homeCatalogs, formTools, editTool

urlpatterns = [
    path('', homeCatalogs, name='activity_catalogs_home'),
    #path('units/', lambda request: None, name='units_list'),
    #path('materials/', lambda request: None, name='materials_list'),
    #path('labours/', lambda request: None, name='labours_list'),
    path('tools/', formTools, name='tools_list'),
    path('tools/edit/<int:tool_id>/', editTool, name='edit_tool'),
]
