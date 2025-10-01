from django.shortcuts import render, get_object_or_404, redirect
from project.models import Project
from .models import Activity, memoryMaterial, memoryLabour, memoryTool
from .forms import ActivityForm, BaseMemoryMaterialFormSet, MemoryMaterialForm
from django.contrib import messages
from django.forms import inlineformset_factory
from django.db import transaction


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
    extra=1,           # usamos empty_form para agregar dinámicamente
    can_delete=True
)

def createActivityInfraestructura(request, pk):
    project = get_object_or_404(Project, pk=pk)

    if request.method == "POST":
        formActivity = ActivityForm(request.POST)

        if formActivity.is_valid():
            with transaction.atomic():
                activity = formActivity.save(commit=False)
                activity.project = project
                activity.save()

                formset = MemoryMaterialFormSet(request.POST, instance=activity)
                if formset.is_valid():
                    formset.save()
                    messages.success(request, "Actividad guardada satisfactoriamente.")
                    return redirect('mainActivityInfraestructura', pk=project.id)
                else:
                    # Si el formset falla, revertimos la actividad creada
                    transaction.set_rollback(True)
        else:
            # Si activity no es válida, crea un formset vacío para re-renderizar con errores
            formset = MemoryMaterialFormSet()

    else:
        formActivity = ActivityForm()
        formset = MemoryMaterialFormSet()  # vacío; renderiza 0 y usas el botón para agregar

    return render(request, 'createActivityInfraestructura.html', {
        "project": project,
        "formActivity": formActivity,
        "formset": formset
    })