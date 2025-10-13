from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.db.models import Q
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.contrib import messages
from project.models import Project
from catalog.models import Material
from .forms import MaterialForm
# Create your views here.

@login_required(login_url='log')
def MainCatalog(request, pk):
    project = get_object_or_404(Project, pk=pk)

    q = (request.GET.get('q') or '').strip()
    page = request.GET.get('page', 1)
    per_page = int(request.GET.get('per_page', 10))

    qs = (Material.objects
          .filter(project=project)
          .select_related('unit')
          .order_by('name'))

    if q:
        # Búsqueda por tokens: cada palabra debe aparecer en algún campo
        for token in q.split():
            qs = qs.filter(
                Q(name__icontains=token) |
                Q(description__icontains=token) |
                Q(unit__abbreviation__icontains=token) |
                Q(unit__name__icontains=token)
            )

    paginator = Paginator(qs, per_page)
    try:
        materials_page = paginator.page(page)
    except PageNotAnInteger:
        materials_page = paginator.page(1)
    except EmptyPage:
        materials_page = paginator.page(paginator.num_pages)

    context = {
        "project": project,
        "materials_page": materials_page,
        "paginator": paginator,
        "is_paginated": paginator.num_pages > 1,
        "per_page": per_page,
        "q": q,
    }
    return render(request, 'mainCatalogs.html', context)

@login_required(login_url='log')
def CreateMaterial(request, pk):
    project = get_object_or_404(Project, pk=pk)

    if request.method == "POST":
        form = MaterialForm(request.POST, project=project)
        if form.is_valid():
            material = form.save(commit=False)
            material.project = project  # asegura la relación
            material.save()
            messages.success(request, "Material creado correctamente.")
            # Cambia 'project_detail' por la vista a la que quieras regresar:
            return redirect('mainCatalog', pk=project.pk)
        else:
            messages.error(request, "Revisa los campos del formulario.")
    else:
        form = MaterialForm(project=project)

    context = {
        "project": project,
        "form": form,
    }
    return render(request, 'formMaterial.html', context)

@login_required(login_url='log')
def EditMaterial(request, pk, material_id):
    project = get_object_or_404(Project, pk=pk)
    material = get_object_or_404(Material, pk=material_id, project=project)

    if request.method == 'POST':
        form = MaterialForm(request.POST, instance=material, project=project)
        if form.is_valid():
            form.save()
            messages.success(request, "Material actualizado correctamente.")
            return redirect('mainCatalog', pk=project.pk)  # ajusta la URL destino
        else:
            messages.error(request, "Corrige los errores del formulario.")
    else:
        form = MaterialForm(instance=material, project=project)

    context = {
        'project': project,
        'form': form,
        'material': material,
        'is_edit': True,  # bandera para distinguir creación/edición
    }
    return render(request, 'formMaterial.html', context)