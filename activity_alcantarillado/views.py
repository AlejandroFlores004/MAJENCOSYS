from django.shortcuts import render
from django.shortcuts import get_object_or_404
from project.models import Project

# Create your views here.
def mainActivityAlcantarillado(request, pk):
    project = get_object_or_404(Project, pk=pk)
    objects = {
        'project': project,
    }
    return render(request, 'mainActivityAlcantarillado.html', objects)