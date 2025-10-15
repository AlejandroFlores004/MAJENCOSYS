from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.db.models import Q
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.contrib import messages
from project.models import Project
from catalog.models import Material, ManoObra, Herramienta, Equipo, Riesgo, Calidad, Ambiental
from .forms import MaterialForm, ManoObraForm, HerramientaForm, EquipoForm, RiesgoForm, CalidadForm, AmbientalForm
# Create your views here.

@login_required(login_url='log')
def MainCatalog(request, pk):
    project = get_object_or_404(Project, pk=pk)

    q_m = (request.GET.get('q_m') or '').strip()
    q_mo = (request.GET.get('q_mo') or '').strip()
    q_hrr = (request.GET.get('q_hrr') or '').strip()
    q_eqp = (request.GET.get('q_eqp') or '').strip()
    q_rsg = (request.GET.get('q_rsg') or '').strip()
    q_cld = (request.GET.get('q_cld') or '').strip()
    q_mbt = (request.GET.get('q_mbt') or '').strip()

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

    # Para Equipo --------------------------------------------------

    qeqp = (Equipo.objects
          .filter(project=project)
          .order_by('name'))
    
    if q_eqp:
        # Búsqueda por tokens: cada palabra debe aparecer en algún campo
        for token in q_eqp.split():
            qeqp = qeqp.filter(
                Q(name__icontains=token) |
                Q(tipo__icontains=token)
            )

    paginatoreqp = Paginator(qeqp, per_page)
    try:
        equipo_page = paginatoreqp.page(page)
    except PageNotAnInteger:
        equipo_page = paginatoreqp.page(1)
    except EmptyPage:
        equipo_page = paginatoreqp.page(paginatoreqp.num_pages)

    # Para Riesgo --------------------------------------------------

    qrsg = (Riesgo.objects
          .filter(project=project)
          .order_by('name'))
    
    if q_rsg:
        # Búsqueda por tokens: cada palabra debe aparecer en algún campo
        for token in q_rsg.split():
            qrsg = qrsg.filter(
                Q(name__icontains=token) |
                Q(peligros__icontains=token) |
                Q(tipo__icontains=token) |
                Q(nivel__icontains=token)
            )

    paginatorrsg = Paginator(qrsg, per_page)
    try:
        riesgo_page = paginatorrsg.page(page)
    except PageNotAnInteger:
        riesgo_page = paginatorrsg.page(1)
    except EmptyPage:
        materials_page = paginatorm.page(paginatorm.num_pages)

    # Para Control de calidad --------------------------------------------------

    qcld = (Calidad.objects
          .filter(project=project)
          .order_by('name'))
    
    if q_cld:
        # Búsqueda por tokens: cada palabra debe aparecer en algún campo
        for token in q_cld.split():
            qcld = qcld.filter(
                Q(name__icontains=token) |
                Q(description__icontains=token) |
                Q(norma__icontains=token) |
                Q(tipo__icontains=token)
            )

    paginatorcld = Paginator(qcld, per_page)
    try:
        calidad_page = paginatorcld.page(page)
    except PageNotAnInteger:
        calidad_page = paginatorcld.page(1)
    except EmptyPage:
        calidad_page = paginatorcld.page(paginatorcld.num_pages)

    # Para Control ambiental --------------------------------------------------

    qmbt = (Ambiental.objects
          .filter(project=project)
          .order_by('name'))
    
    if q_mbt:
        # Búsqueda por tokens: cada palabra debe aparecer en algún campo
        for token in q_mbt.split():
            qmbt = qmbt.filter(
                Q(name__icontains=token) |
                Q(description__icontains=token) |
                Q(epoca__icontains=token) |
                Q(especie__icontains=token)
            )

    paginatormbt = Paginator(qmbt, per_page)
    try:
        ambiental_page = paginatormbt.page(page)
    except PageNotAnInteger:
        ambiental_page = paginatormbt.page(1)
    except EmptyPage:
        ambiental_page = paginatormbt.page(paginatormbt.num_pages)

    context = {
        "project": project,
        "materials_page": materials_page,
        "manoobra_page": manoobra_page,
        "herramienta_page": herramienta_page,
        "equipo_page": equipo_page,
        "riesgo_page": riesgo_page,
        "calidad_page": calidad_page,
        "ambiental_page": ambiental_page,
        "paginatorm": paginatorm,
        "paginatormo": paginatormo,
        "paginatorhrr": paginatorhrr,
        "paginatoreqp": paginatoreqp,
        "paginatorrsg": paginatorrsg,
        "paginatorcld": paginatorcld,
        "paginatormbt": paginatormbt,
        "is_paginatedm": paginatorm.num_pages > 1,
        "is_paginatedmo": paginatormo.num_pages > 1,
        "is_paginatedhrr": paginatorhrr.num_pages > 1,
        "is_paginatedeqp": paginatoreqp.num_pages > 1,
        "is_paginatedrsg": paginatorrsg.num_pages > 1,
        "is_paginatedcld": paginatorcld.num_pages > 1,
        "is_paginatedmbt": paginatormbt.num_pages > 1,
        "per_page": per_page,
        "q_m": q_m,
        "q_mo": q_mo,
        "q_hrr": q_hrr,
        "q_eqp": q_eqp,
        "q_rsg": q_rsg,
        "q_cld": q_cld,
        "q_mbt": q_mbt,
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

@login_required(login_url='log')
def CreateEquipo(request, pk):
    project = get_object_or_404(Project, pk=pk)

    if request.method == "POST":
        form = EquipoForm(request.POST, project=project)
        if form.is_valid():
            Equipo = form.save(commit=False)
            Equipo.project = project  # asegura la relación
            Equipo.save()
            messages.success(request, "Equipo creado correctamente.")
            # Cambia 'project_detail' por la vista a la que quieras regresar:
            return redirect('mainCatalog', pk=project.pk)
        else:
            messages.error(request, "Revisa los campos del formulario.")
    else:
        form = EquipoForm(project=project)

    context = {
        "project": project,
        "form": form,
    }
    return render(request, 'formEquipo.html', context)

@login_required(login_url='log')
def EditEquipo(request, pk, equipo_id):
    project = get_object_or_404(Project, pk=pk)
    equipo = get_object_or_404(Equipo, pk=equipo_id, project=project)

    if request.method == 'POST':
        form = EquipoForm(request.POST, instance=equipo, project=project)
        if form.is_valid():
            form.save()
            messages.success(request, "Equipo actualizado correctamente.")
            return redirect('mainCatalog', pk=project.pk)  # ajusta la URL destino
        else:
            messages.error(request, "Corrige los errores del formulario.")
    else:
        form = EquipoForm(instance=equipo, project=project)

    context = {
        'project': project,
        'form': form,
        'equipo': equipo,
        'is_edit': True,  # bandera para distinguir creación/edición
    }
    return render(request, 'formEquipo.html', context)

@login_required(login_url='log')
def CreateRiesgo(request, pk):
    project = get_object_or_404(Project, pk=pk)

    if request.method == "POST":
        form = RiesgoForm(request.POST, project=project)
        if form.is_valid():
            Riesgo = form.save(commit=False)
            Riesgo.project = project  # asegura la relación
            Riesgo.save()
            messages.success(request, "Riesgo creado correctamente.")
            # Cambia 'project_detail' por la vista a la que quieras regresar:
            return redirect('mainCatalog', pk=project.pk)
        else:
            messages.error(request, "Revisa los campos del formulario.")
    else:
        form = RiesgoForm(project=project)

    context = {
        "project": project,
        "form": form,
    }
    return render(request, 'formRiesgo.html', context)

@login_required(login_url='log')
def EditRiesgo(request, pk, riesgo_id):
    project = get_object_or_404(Project, pk=pk)
    riesgo = get_object_or_404(Riesgo, pk=riesgo_id, project=project)

    if request.method == 'POST':
        form = RiesgoForm(request.POST, instance=riesgo, project=project)
        if form.is_valid():
            form.save()
            messages.success(request, "Riesgo actualizado correctamente.")
            return redirect('mainCatalog', pk=project.pk)  # ajusta la URL destino
        else:
            messages.error(request, "Corrige los errores del formulario.")
    else:
        form = RiesgoForm(instance=riesgo, project=project)

    context = {
        'project': project,
        'form': form,
        'riesgo': riesgo,
        'is_edit': True,  # bandera para distinguir creación/edición
    }
    return render(request, 'formRiesgo.html', context)

@login_required(login_url='log')
def CreateCalidad(request, pk):
    project = get_object_or_404(Project, pk=pk)

    if request.method == "POST":
        form = CalidadForm(request.POST, project=project)
        if form.is_valid():
            Calidad = form.save(commit=False)
            Calidad.project = project  # asegura la relación
            Calidad.save()
            messages.success(request, "Control de calidad creado correctamente.")
            # Cambia 'project_detail' por la vista a la que quieras regresar:
            return redirect('mainCatalog', pk=project.pk)
        else:
            messages.error(request, "Revisa los campos del formulario.")
    else:
        form = CalidadForm(project=project)

    context = {
        "project": project,
        "form": form,
    }
    return render(request, 'formCalidad.html', context)

@login_required(login_url='log')
def EditCalidad(request, pk, calidad_id):
    project = get_object_or_404(Project, pk=pk)
    calidad = get_object_or_404(Calidad, pk=calidad_id, project=project)

    if request.method == 'POST':
        form = CalidadForm(request.POST, instance=calidad, project=project)
        if form.is_valid():
            form.save()
            messages.success(request, "Control de calidad actualizado correctamente.")
            return redirect('mainCatalog', pk=project.pk)  # ajusta la URL destino
        else:
            messages.error(request, "Corrige los errores del formulario.")
    else:
        form = CalidadForm(instance=calidad, project=project)

    context = {
        'project': project,
        'form': form,
        'calidad': calidad,
        'is_edit': True,  # bandera para distinguir creación/edición
    }
    return render(request, 'formCalidad.html', context)

@login_required(login_url='log')
def CreateAmbiental(request, pk):
    project = get_object_or_404(Project, pk=pk)

    if request.method == "POST":
        form = AmbientalForm(request.POST, project=project)
        if form.is_valid():
            Ambiental = form.save(commit=False)
            Ambiental.project = project  # asegura la relación
            Ambiental.save()
            messages.success(request, "Control ambiental creado correctamente.")
            # Cambia 'project_detail' por la vista a la que quieras regresar:
            return redirect('mainCatalog', pk=project.pk)
        else:
            messages.error(request, "Revisa los campos del formulario.")
    else:
        form = AmbientalForm(project=project)

    context = {
        "project": project,
        "form": form,
    }
    return render(request, 'formAmbiental.html', context)

@login_required(login_url='log')
def EditAmbiental(request, pk, ambiental_id):
    project = get_object_or_404(Project, pk=pk)
    ambiental = get_object_or_404(Ambiental, pk=ambiental_id, project=project)

    if request.method == 'POST':
        form = AmbientalForm(request.POST, instance=ambiental, project=project)
        if form.is_valid():
            form.save()
            messages.success(request, "Ambiental actualizado correctamente.")
            return redirect('mainCatalog', pk=project.pk)  # ajusta la URL destino
        else:
            messages.error(request, "Corrige los errores del formulario.")
    else:
        form = AmbientalForm(instance=ambiental, project=project)

    context = {
        'project': project,
        'form': form,
        'ambiental': ambiental,
        'is_edit': True,  # bandera para distinguir creación/edición
    }
    return render(request, 'formAmbiental.html', context)
