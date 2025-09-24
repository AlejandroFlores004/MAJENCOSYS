from django.shortcuts import render, get_object_or_404
from project.models import Project

# Create your views here.
def mainActivityInfraestructura(request, pk):
    project = get_object_or_404(Project, pk=pk)
    objects = {
        'project': project
        }
    return render(request, 'mainActivityInfraestructura.html', objects)