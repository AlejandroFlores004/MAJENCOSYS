# Librerías estándar
from django.shortcuts import get_object_or_404, redirect, render
from django.core.paginator import EmptyPage, PageNotAnInteger, Paginator
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.db import transaction
from django.db.models import (
    Case, Count, DecimalField, DurationField, ExpressionWrapper,
    F, IntegerField, Prefetch, Sum, Value, When
)
from django.db.models.functions import Coalesce
from django.utils import timezone
from django.db.models.functions import Abs

# Modelos del proyecto
from project.models import Project
from schedule.models import Schedule
from .models import (
    Activity, Header, MemoryAmbiental, MemoryCalidad, MemoryEquipo,
    MemoryHerramienta, MemoryManoObra, MemoryMaterial, MemoryRiesgos
)

# Formularios del módulo actual
from .forms import (
    ActivityForm, HeaderFormSet, MemoryAmbientalFormSet, MemoryCalidadFormSet,
    MemoryEquipoFormSet, MemoryHerramientaFormSet, MemoryHidrologica, MemoryHidrologicaFormSet,
    MemoryManoObraFormSet, MemoryMaterialFormSet, MemoryRiesgosFormSet, ScheduleForm
)

# Create your views here.
@login_required(login_url='log')
def mainActivy(request, pk):
    project = get_object_or_404(Project, pk=pk)

    page = request.GET.get('page', 1)
    per_page = int(request.GET.get('per_page', 5))
    q = (request.GET.get('q') or '').strip()

    base_qs = Activity.objects.filter(project=project)

    if q:
        base_qs = base_qs.filter(name__icontains=q)

    today = timezone.localdate()

    qs = (
        base_qs
        .annotate(
            # --- TUS ANOTACIONES ---
            mm_rows=Count('memoryMaterial_activity', distinct=True),
            mm_qty=Coalesce(
                Sum('memoryMaterial_activity__quantity'),
                Value(0),
                output_field=DecimalField(max_digits=12, decimal_places=2)
            ),
            mmo_rows=Count('MemoryManoObra_activity', distinct=True),
            mmo_prestaciones=Coalesce(
                Sum('MemoryManoObra_activity__prestaciones'),
                Value(0),
                output_field=DecimalField(max_digits=12, decimal_places=2)
            ),
            mmo_rendimiento=Coalesce(
                Sum('MemoryManoObra_activity__rendimiento'),
                Value(0),
                output_field=DecimalField(max_digits=12, decimal_places=2)
            ),

            # --- ORDEN POR PROXIMIDAD A HOY ---
            # Trae la fecha de inicio del schedule (puede ser NULL)
            sched_start=F("schedule_activity__start_date"),

            # Diferencia cuando es futuro/igual (>= hoy): start - hoy
            future_delta=ExpressionWrapper(
                F("schedule_activity__start_date") - Value(today),
                output_field=DurationField(),
            ),
            # Diferencia cuando es pasado (< hoy): hoy - start
            past_delta=ExpressionWrapper(
                Value(today) - F("schedule_activity__start_date"),
                output_field=DurationField(),
            ),
            # Tomamos el valor absoluto vía CASE (compatible en Postgres y MySQL)
            abs_delta=Case(
                When(schedule_activity__start_date__isnull=True, then=Value(None)),
                When(schedule_activity__start_date__gte=today, then=F("future_delta")),
                default=F("past_delta"),
                output_field=DurationField(),
            ),
            # Flag para empujar sin-schedule al final
            has_schedule=Case(
                When(schedule_activity__start_date__isnull=True, then=Value(1)),
                default=Value(0),
                output_field=IntegerField(),
            ),
        )
        # Primero las que sí tienen schedule, luego por más cercano a hoy, y como tie-breaker por fecha
        .order_by("has_schedule", "abs_delta", "sched_start", "-id")
        .prefetch_related(
            Prefetch(
                'header_activity',
                queryset=Header.objects.only('id', 'name', 'content', 'activity_id').order_by('id')
            )
        )
    )

    paginator = Paginator(qs, per_page)

    if paginator.count == 0:
        activities_page = None
        is_paginated = False
    else:
        try:
            activities_page = paginator.page(page)
        except PageNotAnInteger:
            activities_page = paginator.page(1)
        except EmptyPage:
            activities_page = paginator.page(paginator.num_pages)
        is_paginated = paginator.num_pages > 1


    context = {
        "project": project,
        "activities_page": activities_page,
        "paginator_activities": paginator,
        "is_paginated_activities": is_paginated,
        "per_page_activities": per_page,

        "q": q,  # por si lo usas en el buscador
    }
    return render(request, 'mainActivities.html', context)

@login_required(login_url='log')
def crearActivity(request, pk):
    project = get_object_or_404(Project, pk=pk)
    activity = Activity(project=project)

    if request.method == "POST":
        form = ActivityForm(request.POST, instance=activity)
        formset = HeaderFormSet(request.POST, instance=activity, prefix="headers")
        # 👇 inyecta la activity en la instancia del form ANTES de validar
        schedule_form = ScheduleForm(request.POST, instance=Schedule(activity=activity), prefix="schedule")

        if form.is_valid() and formset.is_valid() and schedule_form.is_valid():
            try:
                with transaction.atomic():
                    activity = form.save()
                    formset.instance = activity
                    formset.save()

                    sched = schedule_form.save(commit=False)
                    # (ya viene con activity, pero por si acaso:)
                    if sched.activity_id is None:
                        sched.activity = activity
                    sched.save()

                messages.success(request, "Actividad y cronograma creados correctamente.")
                return redirect("mainAcivity", pk=project.pk)
            except Exception:
                form.add_error(None, "No se pudo guardar la actividad y/o el cronograma. Verifique los datos.")
    else:
        form = ActivityForm(instance=activity)
        formset = HeaderFormSet(instance=activity, prefix="headers")
        schedule_form = ScheduleForm(instance=Schedule(activity=activity), prefix="schedule")  # opcional, para precargar

    return render(request, "formActivity.html", {
        "project": project,
        "form": form,
        "formset": formset,
        "schedule_form": schedule_form,
        "is_edit": False,
    })

@login_required(login_url='log')
def editarActivity(request, pk, activity_id):
    project = get_object_or_404(Project, pk=pk)
    activity = get_object_or_404(Activity, pk=activity_id, project=project)

    # Traer schedule existente si hay
    existing_schedule =Schedule.objects.filter(activity=activity).first()

    if request.method == "POST":
        form = ActivityForm(request.POST, instance=activity)
        formset = HeaderFormSet(request.POST, instance=activity, prefix="headers")
        schedule_form = ScheduleForm(request.POST, instance=existing_schedule, prefix="schedule")

        if form.is_valid() and formset.is_valid() and schedule_form.is_valid():
            try:
                with transaction.atomic():
                    form.save()
                    formset.save()

                    sched = schedule_form.save(commit=False)

                    # 👇 Forzar estado a PLANEADO en cada edición
                    sched.status = Schedule.Status.PLANEADO

                    # Si no existía, ligarlo a la actividad
                    if sched.activity_id is None:
                        sched.activity = activity

                    sched.save()

                messages.success(request, "Actividad y cronograma actualizados correctamente (estado forzado a Planeado).")
                return redirect("mainAcivity", pk=project.pk)

            except Exception:
                form.add_error(None, "No se pudo guardar la actividad y/o el cronograma. Verifique los datos.")
    else:
        form = ActivityForm(instance=activity)
        formset = HeaderFormSet(instance=activity, prefix="headers")

        # Opcional: mostrar en el formulario el estado preseleccionado como Planeado al entrar a editar
        schedule_form = ScheduleForm(instance=existing_schedule, prefix="schedule")
        try:
            schedule_form.fields["status"].initial = Schedule.Status.PLANEADO
        except Exception:
            pass

    ctx = {
        "project": project,
        "form": form,
        "formset": formset,
        "schedule_form": schedule_form,
        "activity": activity,
        "is_edit": True,
    }
    return render(request, "formActivity.html", ctx)

@login_required(login_url='log')
def detailActivityPlanned(request, pk, activity_id):
    project = get_object_or_404(Project, pk=pk)
    activity = get_object_or_404(Activity, pk=activity_id, project=project)
    sc = get_object_or_404(Schedule, activity=activity)

    headers = Header.objects.filter(activity=activity)

    today = timezone.localdate()

    ctx = {
        "project": project,
        "activity": activity,
        "headers": headers,
        "schedule": sc,
    }
    return render(request, "activityDetailPlanned.html", ctx)

@login_required(login_url='log')
def detailActivityFinished(request, pk, activity_id):
    project = get_object_or_404(Project, pk=pk)
    activity = get_object_or_404(Activity, pk=activity_id, project=project)
    sc = get_object_or_404(Schedule, activity=activity)

    headers = Header.objects.filter(activity=activity)

    today = timezone.localdate()

    ctx = {
        "project": project,
        "activity": activity,
        "headers": headers,
        "schedule": sc,
    }
    return render(request, "activityDetailFinished.html", ctx)

@login_required(login_url='log')
def memoryManager(request, pk, activity_id):
    project = get_object_or_404(Project, pk=pk)
    activity = get_object_or_404(Activity, pk=activity_id, project=project)
    sc = get_object_or_404(Schedule, activity=activity)

    headers = Header.objects.filter(activity=activity)
    materials = MemoryMaterial.objects.filter(activity=activity)
    labour = MemoryManoObra.objects.filter(activity=activity)
    herramientas = MemoryHerramienta.objects.filter(activity=activity)
    equipo = MemoryEquipo.objects.filter(activity=activity)
    riesgos = MemoryRiesgos.objects.filter(activity=activity)
    calidad = MemoryCalidad.objects.filter(activity=activity)
    ambiental = MemoryAmbiental.objects.filter(activity=activity)   # <- corrige nombre (antes ambienta)
    hidrologica = MemoryHidrologica.objects.filter(activity=activity)

    today = timezone.localdate()

    

    ctx = {
        "project": project,
        "activity": activity,
        "headers": headers,
        "materials": materials,
        "labour": labour,
        "herramientas": herramientas,
        "equipo": equipo,
        "riesgos": riesgos,
        "calidad": calidad,
        "ambiental": ambiental,
        "hidrologica": hidrologica,
        "schedule": sc,
    }
    return render(request, "memoryManage.html", ctx)

@login_required(login_url='log')
def formMemoryMaterials(request, pk, activity_id):
    project = get_object_or_404(Project, pk=pk)
    activity = get_object_or_404(Activity, pk=activity_id, project=project)

    if request.method == "POST":
        formset = MemoryMaterialFormSet(
            request.POST,
            instance=activity,
            form_kwargs={"project": project},   # << clave
        )
        if formset.is_valid():
            formset.save()
            messages.success(request, "Materiales guardados correctamente.")
            return redirect("memoryMananer", pk=project.pk, activity_id=activity.pk)
        else:
            messages.error(request, "Hay errores en el formulario. Revísalos más abajo.")
    else:
        formset = MemoryMaterialFormSet(
            instance=activity,
            form_kwargs={"project": project},   # << también en GET
        )

    return render(request, "formMemoryMaterial.html", {
        "project": project,
        "activity": activity,
        "formset": formset,
    })

@login_required(login_url='log')
def formMemoryManoObra(request, pk, activity_id):
    project = get_object_or_404(Project, pk=pk)
    activity = get_object_or_404(Activity, pk=activity_id, project=project)

    if request.method == "POST":
        formset = MemoryManoObraFormSet(
            request.POST,
            instance=activity,
            form_kwargs={"project": project},  # pasa el proyecto al formulario
        )
        if formset.is_valid():
            formset.save()
            messages.success(request, "Mano de obra guardada correctamente.")
            return redirect("memoryMananer", pk=project.pk, activity_id=activity.pk)
        else:
            messages.error(request, "Hay errores en el formulario. Revísalos más abajo.")
    else:
        formset = MemoryManoObraFormSet(
            instance=activity,
            form_kwargs={"project": project},  # también en GET
        )

    return render(request, "formMemoryLabour.html", {
        "project": project,
        "activity": activity,
        "formset": formset,
    })

@login_required(login_url='log')
def formMemoryHerramienta(request, pk, activity_id):
    project = get_object_or_404(Project, pk=pk)
    activity = get_object_or_404(Activity, pk=activity_id, project=project)

    if request.method == "POST":
        formset = MemoryHerramientaFormSet(
            request.POST,
            instance=activity,
            form_kwargs={"project": project},  # filtra herramientas por proyecto
        )
        if formset.is_valid():
            formset.save()
            messages.success(request, "Herramientas guardadas correctamente.")
            return redirect("memoryMananer", pk=project.pk, activity_id=activity.pk)
        else:
            messages.error(request, "Hay errores en el formulario. Revísalos más abajo.")
    else:
        formset = MemoryHerramientaFormSet(
            instance=activity,
            form_kwargs={"project": project},  # también en GET
        )

    return render(request, "formMemoryHerramienta.html", {
        "project": project,
        "activity": activity,
        "formset": formset,
    })

@login_required(login_url='log')
def formMemoryEquipo(request, pk, activity_id):
    project = get_object_or_404(Project, pk=pk)
    activity = get_object_or_404(Activity, pk=activity_id, project=project)

    if request.method == "POST":
        formset = MemoryEquipoFormSet(
            request.POST,
            instance=activity,
            form_kwargs={"project": project},  # filtra equipos por proyecto
        )
        if formset.is_valid():
            formset.save()
            messages.success(request, "Equipos guardados correctamente.")
            return redirect("memoryMananer", pk=project.pk, activity_id=activity.pk)
        else:
            messages.error(request, "Hay errores en el formulario. Revísalos más abajo.")
    else:
        formset = MemoryEquipoFormSet(
            instance=activity,
            form_kwargs={"project": project},  # también en GET
        )

    return render(request, "formMemoryEquipo.html", {
        "project": project,
        "activity": activity,
        "formset": formset,
    })

@login_required(login_url='log')
def formMemoryRiesgos(request, pk, activity_id):
    project = get_object_or_404(Project, pk=pk)
    activity = get_object_or_404(Activity, pk=activity_id, project=project)

    if request.method == "POST":
        formset = MemoryRiesgosFormSet(
            request.POST,
            instance=activity,
            form_kwargs={"project": project},  # filtra riesgos por proyecto y fija project en save()
        )
        if formset.is_valid():
            formset.save()  # cada form asigna project en su save()
            messages.success(request, "Riesgos guardados correctamente.")
            return redirect("memoryMananer", pk=project.pk, activity_id=activity.pk)
        else:
            messages.error(request, "Hay errores en el formulario. Revísalos más abajo.")
    else:
        formset = MemoryRiesgosFormSet(
            instance=activity,
            form_kwargs={"project": project},  # también en GET
        )

    return render(request, "formMemoryRiesgos.html", {
        "project": project,
        "activity": activity,
        "formset": formset,
    })

@login_required(login_url='log')
def formMemoryCalidad(request, pk, activity_id):
    project = get_object_or_404(Project, pk=pk)
    activity = get_object_or_404(Activity, pk=activity_id, project=project)

    if request.method == "POST":
        formset = MemoryCalidadFormSet(
            request.POST,
            instance=activity,
            form_kwargs={"project": project},  # filtra 'calidad' por proyecto y fija project en save()
        )
        if formset.is_valid():
            formset.save()  # cada form asigna project en su save()
            messages.success(request, "Controles de calidad guardados correctamente.")
            return redirect("memoryMananer", pk=project.pk, activity_id=activity.pk)
        else:
            messages.error(request, "Hay errores en el formulario. Revísalos más abajo.")
    else:
        formset = MemoryCalidadFormSet(
            instance=activity,
            form_kwargs={"project": project},  # también en GET
        )

    return render(request, "formMemoryCalidad.html", {
        "project": project,
        "activity": activity,
        "formset": formset,
    })

@login_required(login_url='log')
def formMemoryAmbiental(request, pk, activity_id):
    project = get_object_or_404(Project, pk=pk)
    activity = get_object_or_404(Activity, pk=activity_id, project=project)

    if request.method == "POST":
        formset = MemoryAmbientalFormSet(
            request.POST,
            instance=activity,
            form_kwargs={"project": project},  # filtra 'ambiental' por proyecto y fija project en save()
        )
        if formset.is_valid():
            formset.save()
            messages.success(request, "Controles ambientales guardados correctamente.")
            return redirect("memoryMananer", pk=project.pk, activity_id=activity.pk)
        else:
            messages.error(request, "Hay errores en el formulario. Revísalos más abajo.")
    else:
        formset = MemoryAmbientalFormSet(
            instance=activity,
            form_kwargs={"project": project},  # también en GET
        )

    return render(request, "formMemoryAmbiental.html", {
        "project": project,
        "activity": activity,
        "formset": formset,
    })

@login_required(login_url='log')
def formMemoryHidrologica(request, pk, activity_id):
    project = get_object_or_404(Project, pk=pk)
    activity = get_object_or_404(Activity, pk=activity_id, project=project)

    if request.method == "POST":
        formset = MemoryHidrologicaFormSet(
            request.POST,
            instance=activity,
            form_kwargs={"project": project},  # filtra 'hidrologica' por proyecto y fija project en save()
        )
        if formset.is_valid():
            formset.save()
            messages.success(request, "Pruebas hidrológicas guardadas correctamente.")
            return redirect("memoryMananer", pk=project.pk, activity_id=activity.pk)
        else:
            messages.error(request, "Hay errores en el formulario. Revísalos más abajo.")
    else:
        formset = MemoryHidrologicaFormSet(
            instance=activity,
            form_kwargs={"project": project},  # también en GET
        )

    return render(request, "formMemoryHidrologica.html", {
        "project": project,
        "activity": activity,
        "formset": formset,
    })