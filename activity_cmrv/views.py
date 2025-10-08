from django.shortcuts import render
from project.models import Project
from django.shortcuts import get_object_or_404
from .models import Activity, memoryHeavyMachine, memoryLabour, memoryMaterial, memoryTool
# Create your views here.
def mainActivityCrmv(request, pk):
    project = get_object_or_404(Project, pk=pk)
    activities = Activity.objects.filter(project=project)
    materials = memoryMaterial.objects.filter(activity__in=activities)
    labours = memoryLabour.objects.filter(activity__in=activities)
    tools = memoryTool.objects.filter(activity__in=activities)
    
    return render(request, 'mainActivityInfraestructura.html', {
        'project': project,
        'activities': activities,
        'materials': materials,
        'labours': labours,
        'tools': tools,
    })

