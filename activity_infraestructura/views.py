from django.shortcuts import render, get_object_or_404
from project.models import Project
from .models import Activity, memoryMaterial, memoryLabour, memoryTool

# Create your views here.
def mainActivityInfraestructura(request, pk):
    project = get_object_or_404(Project, pk=pk)
    activities = Activity.objects.filter(project=project)
    materials = memoryMaterial.objects.filter(activity__in=activities)
    labours = memoryLabour.objects.filter(activity__in=activities)
    tools = memoryTool.objects.filter(activity__in=activities)
    objects = {
        'project': project,
        'activities': activities,
        'materials': materials,
        'labours': labours,
        'tools': tools,
    }
    return render(request, 'mainActivityInfraestructura.html', objects)