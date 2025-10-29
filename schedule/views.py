from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.db.models import Prefetch, Q
from django.utils import timezone
from django.contrib import messages

from project.models import Project
from activity.models import Activity, Header
from schedule.models import schedule as Schedule  # tu modelo


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
            Prefetch(
                "schedule_activity",
                queryset=Schedule.objects.order_by("-updated_at", "-id")
            )
        )
        .order_by("name")
    )

    if q:
        activities_qs = activities_qs.filter(Q(name__icontains=q))

    starting_today, ending_today, in_progress, upcoming, finished = [], [], [], [], []

    for ac in activities_qs:
        sch = ac.schedule_activity.first()
        if not sch:
            continue

        if sch.status == Schedule.Status.PLANEADO and sch.start_date == today:
            starting_today.append((ac, sch))  # 1) Empiezan hoy
        elif sch.end_date == today and sch.status in (Schedule.Status.PLANEADO, Schedule.Status.EJECUTANDO):
            ending_today.append((ac, sch))    # 3) Finalizan hoy (no finalizadas)
        elif sch.status == Schedule.Status.EJECUTANDO:
            in_progress.append((ac, sch))     # 2) En curso
        elif sch.status == Schedule.Status.PLANEADO and sch.start_date > today:
            upcoming.append((ac, sch))        # 4) Próximas (futuras)
        elif sch.status == Schedule.Status.FINALIZADO:
            finished.append((ac, sch))        # 5) Finalizadas

    # Ordenes para UI
    starting_today.sort(key=lambda t: (t[1].start_date, t[0].name.lower()))
    in_progress.sort(key=lambda t: (t[1].start_date, t[0].name.lower()))
    ending_today.sort(key=lambda t: (t[1].end_date, t[0].name.lower()))
    upcoming.sort(key=lambda t: (t[1].start_date, t[0].name.lower()))
    finished.sort(key=lambda t: (t[1].end_date or t[1].start_date, t[0].name.lower()), reverse=True)

    context = {
        "project": project,
        "q": q,
        "starting_today": starting_today,
        "in_progress": in_progress,
        "ending_today": ending_today,
        "upcoming": upcoming,      # <-- nuevo
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

        sch.status = Schedule.Status.EJECUTANDO
        sch.save(update_fields=["status", "updated_at"])
        messages.success(request, "La actividad ahora está en estado: Ejecutando.")
        return redirect("schedule_home", pk=pk)

    # GET
    context = {
        "project": project,
        "activity": activity,
        "sch": sch,
        "today": today,
        "can_start_today": can_start_today,
    }
    return render(request, "schedules/start_now.html", context)


def schedule_finish_page(request, pk, activity_id):
    project = get_object_or_404(Project, pk=pk)
    activity = get_object_or_404(Activity, pk=activity_id, project=project)
    sch = activity.schedule_activity.first()

    if not sch:
        messages.error(request, "Esta actividad no tiene cronograma configurado.")
        return redirect("schedule_home", pk=pk)

    today = timezone.localdate()
    # Puede finalizar si su end_date es hoy o ya pasó
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

        # Forzar a FINALIZADO
        sch.status = Schedule.Status.FINALIZADO
        # Si tu modelo tiene updated_at auto_now=True no hace falta, pero por si usas manual:
        try:
            sch.save(update_fields=["status", "updated_at"])
        except Exception:
            sch.save(update_fields=["status"])

        messages.success(request, "La actividad ahora está en estado: Finalizado.")
        return redirect("schedule_home", pk=pk)

    # GET (opcional mostrar confirmación)
    context = {
        "project": project,
        "activity": activity,
        "sch": sch,
        "today": today,
        "can_finish_today": can_finish_today,
    }
    return render(request, "schedules/finish_now.html", context)