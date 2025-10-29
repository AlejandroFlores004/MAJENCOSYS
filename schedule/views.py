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

    # Prefetch ordenado para que .first() nos dé el cronograma más "reciente/útil"
    activities_qs = (
        Activity.objects
        .filter(project=project)
        .prefetch_related(
            Prefetch("header_activity", queryset=Header.objects.all()),
            Prefetch("schedule_activity",
                     queryset=Schedule.objects.order_by(
                         # Prioriza activos/recientes; ajusta a tu gusto
                         "-updated_at", "-id"
                     ))
        )
        .order_by("name")
    )

    if q:
        activities_qs = activities_qs.filter(Q(name__icontains=q))

    starting_today, in_progress, finished = [], [], []

    for ac in activities_qs:
        # Tomamos el primer schedule prefetchado (según el orden definido arriba)
        sch = ac.schedule_activity.first()
        if not sch:
            continue

        # Agrupación según tu regla
        if sch.status == Schedule.Status.PLANEADO and sch.start_date == today:
            starting_today.append((ac, sch))
        elif sch.status == Schedule.Status.EJECUTANDO:
            in_progress.append((ac, sch))
        elif sch.status == Schedule.Status.FINALIZADO:
            finished.append((ac, sch))

    # Ordenes amigables para la UI
    starting_today.sort(key=lambda t: (t[1].start_date, t[0].name.lower()))
    in_progress.sort(key=lambda t: (t[1].start_date, t[0].name.lower()))
    finished.sort(key=lambda t: (t[1].end_date or t[1].start_date, t[0].name.lower()), reverse=True)

    context = {
        "project": project,
        "q": q,
        # Listas de tuplas (actividad, schedule) para el template
        "starting_today": starting_today,
        "in_progress": in_progress,
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