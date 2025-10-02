# views.py
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib import messages
from django.forms import inlineformset_factory
from django.db import transaction

from project.models import Project
from .models import Activity, memoryMaterial, memoryLabour, memoryTool
from .forms import (
    ActivityForm,
    BaseMemoryMaterialFormSet, MemoryMaterialForm,
    BaseMemoryLabourFormSet,  MemoryLabourForm
)


def mainActivityInfraestructura(request, pk):
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


MemoryMaterialFormSet = inlineformset_factory(
    Activity,
    memoryMaterial,
    form=MemoryMaterialForm,
    formset=BaseMemoryMaterialFormSet,
    extra=1,          # 1 fila inicial visible
    can_delete=True
)

MemoryLabourFormSet = inlineformset_factory(
    Activity,
    memoryLabour,
    form=MemoryLabourForm,
    formset=BaseMemoryLabourFormSet,
    extra=1,
    can_delete=True
)


def createActivityInfraestructura(request, pk):
    project = get_object_or_404(Project, pk=pk)

    if request.method == "POST":
        formActivity = ActivityForm(request.POST)

        # Enlaza formsets a una instancia temporal si Activity es inválida
        temp_activity = Activity(project=project)
        materials_formset = MemoryMaterialFormSet(
            request.POST, instance=temp_activity, form_kwargs={'project': project}
        )
        labours_formset = MemoryLabourFormSet(
            request.POST, instance=temp_activity, form_kwargs={'project': project}
        )

        if formActivity.is_valid():
            with transaction.atomic():
                activity = formActivity.save(commit=False)
                activity.project = project
                activity.save()

                # Reinstancia con la actividad real
                materials_formset = MemoryMaterialFormSet(
                    request.POST, instance=activity, form_kwargs={'project': project}
                )
                labours_formset = MemoryLabourFormSet(
                    request.POST, instance=activity, form_kwargs={'project': project}
                )

                # ⚠️ Validar por separado (NO usar "and" para evitar short-circuit)
                valid_materials = materials_formset.is_valid()
                valid_labours   = labours_formset.is_valid()

                if valid_materials and valid_labours:
                    materials_formset.save()
                    labours_formset.save()
                    messages.success(request, "Actividad guardada satisfactoriamente.")
                    return redirect('mainActivityInfraestructura', pk=project.id)
                else:
                    # Añade mensajes por cada formset inválido
                    if not valid_materials:
                        for e in materials_formset.non_form_errors():
                            messages.error(request, f"Materiales: {e}")
                    if not valid_labours:
                        for e in labours_formset.non_form_errors():
                            messages.error(request, f"Mano de obra: {e}")

                    # Marca rollback de la Activity creada
                    transaction.set_rollback(True)

        else:
            # Activity inválida: mensaje general y cae a render con errores
            messages.error(request, "Revisa los datos de la actividad.")

    else:
        formActivity = ActivityForm()
        materials_formset = MemoryMaterialFormSet(form_kwargs={'project': project})
        labours_formset   = MemoryLabourFormSet(form_kwargs={'project': project})

    return render(request, 'createActivityInfraestructura.html', {
        "project": project,
        "formActivity": formActivity,
        "materials_formset": materials_formset,
        "labours_formset": labours_formset
    })
