from django.shortcuts import render, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.db.models import Prefetch, Q

from project.models import Project
from activity.models import Activity, Header
from schedule.models import schedule  # tu modelo

@login_required(login_url='log')
def mainSchedule(request, pk):
    project = get_object_or_404(Project, pk=pk)

    q = (request.GET.get("q") or "").strip()
    try:
        per_page = int(request.GET.get("per_page", 10))
    except ValueError:
        per_page = 10
    if per_page not in (5, 10, 20):
        per_page = 10

    activities_qs = (
        Activity.objects
        .filter(project=project)
        .prefetch_related(
            Prefetch("header_activity", queryset=Header.objects.all()),
            # Traemos el cronograma (uno por actividad según tu UniqueConstraint)
            Prefetch("schedule_activity", queryset=schedule.objects.all())
        )
        .order_by("name")
    )

    if q:
        activities_qs = activities_qs.filter(Q(name__icontains=q))

    paginator = Paginator(activities_qs, per_page)
    page_num = request.GET.get("page", 1)
    try:
        activities_page = paginator.page(page_num)
    except PageNotAnInteger:
        activities_page = paginator.page(1)
    except EmptyPage:
        activities_page = paginator.page(paginator.num_pages)

    context = {
        "project": project,
        "q": q,
        "per_page_activities": per_page,
        "activities_page": activities_page,
        "paginator_activities": paginator,
        "is_paginated_activities": activities_page.has_other_pages(),
    }
    return render(request, "mainSchedule.html", context)
