from django.shortcuts import render, get_object_or_404, redirect
from project.models import Project
from .models import Activity, memoryMaterial, memoryLabour, memoryTool
from .forms import ActivityForm, MemoryMaterialForm
from django.contrib import messages

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

def createActivityInfraestructura(request, pk):
    project = get_object_or_404(Project, pk=pk)

    if request.method == "POST":
        formActivity = ActivityForm(request.POST)
        formMemoryMaterial = MemoryMaterialForm(request.POST, project=project)

        if formActivity.is_valid():
            activity = formActivity.save(commit=False)
            activity.project = project
            activity.save()

            # Guardar un registro de memoria de material si el usuario lo llenó
            if formMemoryMaterial.has_changed() and formMemoryMaterial.is_valid():
                mm = formMemoryMaterial.save(commit=False)
                mm.activity = activity
                mm.save()

            messages.success(request, "Actividad guardada satisfactoriamente.")
            return redirect('mainActivityInfraestructura', pk=project.id)

        # si Activity no es válida, caerá a render con errores de ambos forms
    else:
        formActivity = ActivityForm()
        formMemoryMaterial = MemoryMaterialForm(project=project)

    objects = {
        "project":project,
        "formActivity": formActivity,
        "formMemoryMaterial": formMemoryMaterial
    }
    return render(request,'createActivityInfraestructura.html',objects)