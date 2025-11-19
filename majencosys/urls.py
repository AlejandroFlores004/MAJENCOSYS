
from django.contrib import admin
from django.urls import path,include, re_path
from django.shortcuts import render
from django.conf import settings
from django.conf.urls.static import static


def custom_404_view(request, exception=None):
    """
    Vista simple para mostrar el template 404
    """
    return render(request, '404.html', status=404)


urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('main.urls')),
    path('admon_project/', include('project.urls')),
    
] 
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

# Catch-all pattern para URLs no encontradas
urlpatterns += [
    re_path(r'^.*$', custom_404_view),
]
