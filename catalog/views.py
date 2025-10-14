from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.db.models import Q
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.contrib import messages
from project.models import Project
from catalog.models import Material, ManoObra, Herramienta, Equipo
from .forms import MaterialForm, ManoObraForm, HerramientaForm, EquipoForm
# Create your views here.

@login_required(login_url='log')
def MainCatalog(request, pk):
    project = get_object_or_404(Project, pk=pk)

    q_m = (request.GET.get('q_m') or '').strip()
    q_mo = (request.GET.get('q_mo') or '').strip()
    q_hrr = (request.GET.get('q_hrr') or '').strip()

    page = request.GET.get('page', 1)
    per_page = int(request.GET.get('per_page', 10))

    # Para Materiales ---------------------------------------------------
    
    qm = (Material.objects
          .filter(project=project)
          .select_related('unit')
          .order_by('name'))

    if q_m:
        # Búsqueda por tokens: cada palabra debe aparecer en algún campo
        for token in q_m.split():
            qm = qm.filter(
                Q(name__icontains=token) |
                Q(description__icontains=token) |
                Q(unit__abbreviation__icontains=token) |
                Q(unit__name__icontains=token)
            )

    paginatorm = Paginator(qm, per_page)
    try:
        materials_page = paginatorm.page(page)
    except PageNotAnInteger:
        materials_page = paginatorm.page(1)
    except EmptyPage:
        materials_page = paginatorm.page(paginatorm.num_pages)

    # Para Mano de obra --------------------------------------------------

    qmo = (ManoObra.objects
          .filter(project=project)
          .order_by('name'))
    
    if q_mo:
        # Búsqueda por tokens: cada palabra debe aparecer en algún campo
        for token in q_mo.split():
            qmo = qmo.filter(
                Q(name__icontains=token) |
                Q(description__icontains=token)
            )

    paginatormo = Paginator(qmo, per_page)
    try:
        manoobra_page = paginatormo.page(page)
    except PageNotAnInteger:
        manoobra_page = paginatormo.page(1)
    except EmptyPage:
        manoobra_page = paginatormo.page(paginatormo.num_pages)

    # Para Herramientas --------------------------------------------------

    qhrr = (Herramienta.objects
          .filter(project=project)
          .order_by('name'))
    
    if q_hrr:
        # Búsqueda por tokens: cada palabra debe aparecer en algún campo
        for token in q_hrr.split():
            qhrr = qhrr.filter(
                Q(name__icontains=token) |
                Q(tipo__icontains=token)
            )

    paginatorhrr = Paginator(qhrr, per_page)
    try:
        herramienta_page = paginatorhrr.page(page)
    except PageNotAnInteger:
        herramienta_page = paginatorhrr.page(1)
    except EmptyPage:
        herramienta_page = paginatorhrr.page(paginatorhrr.num_pages)

    context = {
        "project": project,
        "materials_page": materials_page,
        "manoobra_page": manoobra_page,
        "herramienta_page": herramienta_page,
        "paginatorm": paginatorm,
        "paginatormo": paginatormo,
        "paginatorhrr": paginatorhrr,
        "is_paginatedm": paginatorm.num_pages > 1,
        "is_paginatedmo": paginatormo.num_pages > 1,
        "is_paginatedhrr": paginatorhrr.num_pages > 1,
        "per_page": per_page,
        "q_m": q_m,
        "q_mo": q_mo,
        "q_hrr": q_hrr,
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

@login_required(login_url='log')
def CreateManoObra(request, pk):
    project = get_object_or_404(Project, pk=pk)

    if request.method == "POST":
        form = ManoObraForm(request.POST, project=project)
        if form.is_valid():
            ManoObra = form.save(commit=False)
            ManoObra.project = project  # asegura la relación
            ManoObra.save()
            messages.success(request, "Mano de obra creado correctamente.")
            # Cambia 'project_detail' por la vista a la que quieras regresar:
            return redirect('mainCatalog', pk=project.pk)
        else:
            messages.error(request, "Revisa los campos del formulario.")
    else:
        form = ManoObraForm(project=project)

    context = {
        "project": project,
        "form": form,
    }
    return render(request, 'formManoObra.html', context)

@login_required(login_url='log')
def EditManoObra(request, pk, manoobra_id):
    project = get_object_or_404(Project, pk=pk)
    manoobra = get_object_or_404(ManoObra, pk=manoobra_id, project=project)

    if request.method == 'POST':
        form = ManoObraForm(request.POST, instance=manoobra, project=project)
        if form.is_valid():
            form.save()
            messages.success(request, "Mano de obra actualizado correctamente.")
            return redirect('mainCatalog', pk=project.pk)  # ajusta la URL destino
        else:
            messages.error(request, "Corrige los errores del formulario.")
    else:
        form = ManoObraForm(instance=manoobra, project=project)

    context = {
        'project': project,
        'form': form,
        'manoobra': manoobra,
        'is_edit': True,  # bandera para distinguir creación/edición
    }
    return render(request, 'formManoObra.html', context)

@login_required(login_url='log')
def CreateHerramienta(request, pk):
    project = get_object_or_404(Project, pk=pk)

    if request.method == "POST":
        form = HerramientaForm(request.POST, project=project)
        if form.is_valid():
            Herramienta = form.save(commit=False)
            Herramienta.project = project  # asegura la relación
            Herramienta.save()
            messages.success(request, "Herramienta creado correctamente.")
            # Cambia 'project_detail' por la vista a la que quieras regresar:
            return redirect('mainCatalog', pk=project.pk)
        else:
            messages.error(request, "Revisa los campos del formulario.")
    else:
        form = HerramientaForm(project=project)

    context = {
        "project": project,
        "form": form,
    }
    return render(request, 'formHerramienta.html', context)

@login_required(login_url='log')
def EditHerramienta(request, pk, herramienta_id):
    project = get_object_or_404(Project, pk=pk)
    herramienta = get_object_or_404(Herramienta, pk=herramienta_id, project=project)

    if request.method == 'POST':
        form = HerramientaForm(request.POST, instance=herramienta, project=project)
        if form.is_valid():
            form.save()
            messages.success(request, "Herramienta actualizado correctamente.")
            return redirect('mainCatalog', pk=project.pk)  # ajusta la URL destino
        else:
            messages.error(request, "Corrige los errores del formulario.")
    else:
        form = HerramientaForm(instance=herramienta, project=project)

    context = {
        'project': project,
        'form': form,
        'herramienta': herramienta,
        'is_edit': True,  # bandera para distinguir creación/edición
    }
    return render(request, 'formHerramienta.html', context)
