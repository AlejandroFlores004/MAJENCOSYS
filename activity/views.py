from django.shortcuts import render, get_object_or_404, redirect
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from project.models import Project
from .models import Activity, Header, MemoryMaterial
from django.db.models import Prefetch, Count, Sum, Value, DecimalField
from django.db.models.functions import Coalesce
from catalog.models import Material
from django.contrib.auth.decorators import login_required

from project.models import Project
from .models import Activity
from .forms import ActivityForm, HeaderFormSet
from django.contrib import messages


# Create your views here.
@login_required(login_url='log')
def mainActivy(request, pk):
    project = get_object_or_404(Project, pk=pk)

    page = request.GET.get('page', 1)
    per_page = int(request.GET.get('per_page', 5))

    qs = (
        Activity.objects
        .filter(project=project)
        .annotate(
            mm_rows=Count('memoryMaterial_activity', distinct=True),
            mm_qty=Coalesce(
                Sum('memoryMaterial_activity__quantity'),
                Value(0),  # <- valor por defecto
                output_field=DecimalField(max_digits=12, decimal_places=2)
            ),
        )
        .order_by('-id')
        .prefetch_related(
            Prefetch(
                'header_activity',
                queryset=Header.objects.only('id', 'name', 'content', 'activity_id').order_by('id')
            )
        )
    )

    paginator = Paginator(qs, per_page)
    try:
        activities_page = paginator.page(page)
    except PageNotAnInteger:
        activities_page = paginator.page(1)
    except EmptyPage:
        activities_page = paginator.page(paginator.num_pages)

    countMaterial = Material.objects.filter(project=project).count()

    context = {
        "project": project,
        "activities_page": activities_page,
        "paginator_activities": paginator,
        "is_paginated_activities": paginator.num_pages > 1,
        "per_page_activities": per_page,
        "quiantyMaterial": countMaterial,
    }

    return render(request, 'mainActivities.html', context)

@login_required(login_url='log')
def crearActivity(request, pk):
    project = get_object_or_404(Project, pk=pk)

    # Preasignamos el proyecto a la instancia (no tiene PK todavía)
    activity = Activity(project=project)

    if request.method == "POST":
        form = ActivityForm(request.POST, instance=activity)
        formset = HeaderFormSet(request.POST, instance=activity, prefix="headers")
        if form.is_valid() and formset.is_valid():
            # Guarda la actividad para que tenga PK
            activity = form.save()
            # Guarda encabezados ligados a esa actividad
            formset.instance = activity
            formset.save()
            messages.success(request, "Actividad creada correctamente.")
            # Ajusta el redirect a tu vista de detalle/listado
            return redirect("mainAcivity", pk=project.pk)
    else:
        form = ActivityForm(instance=activity)
        formset = HeaderFormSet(instance=activity, prefix="headers")

    ctx = {
        "project": project,
        "form": form,
        "formset": formset,
    }
    return render(request, "formActivity.html", ctx)