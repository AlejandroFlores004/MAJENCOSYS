from django.shortcuts import render, get_object_or_404, redirect
from project.models import Project
from .models import Activity, memoryMaterial, memoryLabour, memoryTool
from .forms import ActivityForm, BaseMemoryMaterialFormSet, MemoryMaterialForm
from django.contrib import messages
from django.forms import inlineformset_factory

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


MemoryMaterialFormSet = inlineformset_factory(
    Activity,
    memoryMaterial,
    form=MemoryMaterialForm,
    formset=BaseMemoryMaterialFormSet,
    extra=2,
    can_delete=True
)

def createActivityInfraestructura(request, pk):
    project = get_object_or_404(Project, pk=pk)

    if request.method == "POST":
        formActivity = ActivityForm(request.POST)
        formset = MemoryMaterialFormSet(request.POST)

        if formActivity.is_valid():
            activity = formActivity.save(commit=False)
            activity.project = project
            activity.save()

            # Importante: asociar los materiales a la activity
            formset.instance = activity
            formset.save()

            messages.success(request, "Actividad guardada satisfactoriamente.")
            return redirect('mainActivityInfraestructura', pk=project.id)

        # si Activity no es válida, caerá a render con errores de ambos forms
    else:
        formActivity = ActivityForm()
        formset = MemoryMaterialFormSet(queryset=memoryMaterial.objects.none(), project=project)

    objects = {
        "project":project,
        "formActivity": formActivity,
        "formset": formset
    }
    return render(request,'createActivityInfraestructura.html',objects)