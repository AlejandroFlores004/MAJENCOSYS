from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.db.models import Prefetch, Q
from django.utils import timezone
from django.contrib import messages
from django.db import transaction

from project.models import Project
from activity.models import Activity, Header
from schedule.models import Schedule   # tu modelo


@login_required(login_url='log')
def mainSchedule(request, pk):
    project = get_object_or_404(Project, pk=pk)
    q = (request.GET.get("q") or "").strip()
    today = timezone.localdate()

    activities_qs = (
        Activity.objects
        .filter(project=project)
        .prefetch_related(
            Prefetch("header_activity", queryset=Header.objects.all()),
            Prefetch("schedule_activity", queryset=Schedule.objects.order_by("-updated_at", "-id"))
        )
        .order_by("name")
    )
    if q:
        activities_qs = activities_qs.filter(Q(name__icontains=q))

    to_start, in_progress, to_finish, upcoming, finished = [], [], [], [], []

    for ac in activities_qs:
        sch = ac.schedule_activity.first()
        if not sch:
            continue

        # 1) Terminar: vencidas (end_date <= hoy) y NO finalizadas
        if sch.end_date and sch.end_date <= today and sch.status in (Schedule.Status.PLANEADO, Schedule.Status.EJECUTANDO):
            to_finish.append((ac, sch))
            continue

        # 2) En curso: ejecutando y no vencidas
        if sch.status == Schedule.Status.EJECUTANDO:
            in_progress.append((ac, sch))
            continue

        # 3) Iniciar: planeadas con start_date <= hoy
        if sch.status == Schedule.Status.PLANEADO and sch.start_date and sch.start_date <= today:
            to_start.append((ac, sch))
            continue

        # 4) Futuras: planeadas con start_date > hoy
        if sch.status == Schedule.Status.PLANEADO and sch.start_date and sch.start_date > today:
            upcoming.append((ac, sch))
            continue

        # 5) Finalizadas
        if sch.status == Schedule.Status.FINALIZADO:
            finished.append((ac, sch))

    # Orden UI
    to_start.sort(key=lambda t: (t[1].start_date, t[0].name.lower()))
    in_progress.sort(key=lambda t: (t[1].start_date, t[0].name.lower()))
    to_finish.sort(key=lambda t: (t[1].end_date or t[1].start_date, t[0].name.lower()))
    upcoming.sort(key=lambda t: (t[1].start_date, t[0].name.lower()))
    finished.sort(key=lambda t: (t[1].end_date or t[1].start_date, t[0].name.lower()), reverse=True)

    context = {
        "project": project,
        "q": q,
        "to_start": to_start,
        "in_progress": in_progress,
        "to_finish": to_finish,
        "upcoming": upcoming,
        "finished": finished,
    }
    return render(request, "mainSchedule.html", context)

@login_required(login_url='log')
def schedule_start_page(request, pk, activity_id):
    project = get_object_or_404(Project, pk=pk)
    activity = get_object_or_404(Activity, pk=activity_id, project=project)
    sch = activity.schedule_activity.first()

    if not sch:
        messages.error(request, "Esta actividad no tiene cronograma configurado.")
        return redirect("schedule_home", pk=pk)

    today = timezone.localdate()
    can_start_today = (sch.start_date <= today) and (sch.status == Schedule.Status.PLANEADO)

    if request.method == "POST":
        if sch.status != Schedule.Status.PLANEADO:
            messages.warning(request, "La actividad no está en estado Planeado.")
            return redirect("schedule_start_page", pk=pk, activity_id=activity_id)

        if sch.start_date > today:
            messages.warning(
                request,
                f"Aún no es la fecha de inicio (empieza el {sch.start_date.strftime('%d/%m/%Y')})."
            )
            return redirect("schedule_start_page", pk=pk, activity_id=activity_id)

        # Cambiar a EJECUTANDO y fijar real_start_date si no existe
        with transaction.atomic():
            sch.status = Schedule.Status.EJECUTANDO
            if not sch.real_start_date:
                sch.real_start_date = today
                sch.save(update_fields=["status", "real_start_date", "updated_at"])
            else:
                sch.save(update_fields=["status", "updated_at"])

        messages.success(request, "La actividad ahora está en estado: Ejecutando (fecha real de inicio guardada).")
        return redirect("schedule_home", pk=pk)

    # GET
    context = {
        "project": project,
        "activity": activity,
        "sch": sch,
        "today": today,
        "can_start_today": can_start_today,
    }
    return render(request, "start_now.html", context)


@login_required(login_url='log')
def schedule_finish_page(request, pk, activity_id):
    project = get_object_or_404(Project, pk=pk)
    activity = get_object_or_404(Activity, pk=activity_id, project=project)
    sch = activity.schedule_activity.first()

    if not sch:
        messages.error(request, "Esta actividad no tiene cronograma configurado.")
        return redirect("schedule_home", pk=pk)

    today = timezone.localdate()
    # Puede finalizar si su end_date es hoy o ya pasó y no está finalizado aún
    can_finish_today = (sch.end_date <= today) and (sch.status in (Schedule.Status.PLANEADO, Schedule.Status.EJECUTANDO))

    if request.method == "POST":
        if sch.status == Schedule.Status.FINALIZADO:
            messages.info(request, "La actividad ya está finalizada.")
            return redirect("schedule_home", pk=pk)

        if sch.end_date > today:
            messages.warning(
                request,
                f"Aún no es la fecha de fin (termina el {sch.end_date.strftime('%d/%m/%Y')})."
            )
            return redirect("schedule_finish_page", pk=pk, activity_id=activity_id)

        # Finalizar y fijar real_end_date si no existe
        with transaction.atomic():
            sch.status = Schedule.Status.FINALIZADO
            update_fields = ["status", "updated_at"]

            if not sch.real_end_date:
                sch.real_end_date = today
                update_fields.insert(1, "real_end_date")  # mantener orden lógico

            try:
                sch.save(update_fields=update_fields)
            except Exception:
                sch.save()

        messages.success(request, "La actividad ahora está en estado: Finalizado (fecha real de fin guardada).")
        return redirect("schedule_home", pk=pk)

    # GET (página de confirmación)
    context = {
        "project": project,
        "activity": activity,
        "sch": sch,
        "today": today,
        "can_finish_today": can_finish_today,
    }
    return render(request, "finish_now.html", context)