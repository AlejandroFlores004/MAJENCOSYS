# project/views.py
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, get_object_or_404, redirect
from django.core.paginator import Paginator, EmptyPage
from django.contrib import messages
from django.db.models import Q

from .models import Project
from .forms import ProjectForm


@login_required(login_url='log')
def projectMain(request):
    qs = Project.objects.select_related("usuario", "tecnico").order_by("-created_at")

    q = (request.GET.get("q") or "").strip()
    t = (request.GET.get("type") or "").strip()
    e = (request.GET.get("estado") or "").strip()

    if q:
        qs = qs.filter(Q(nombre__icontains=q) | Q(cliente__icontains=q))
    if t:
        qs = qs.filter(type=t)
    if e:
        qs = qs.filter(estado=e)

    paginator = Paginator(qs, 7)  # 7 por página
    page_number = request.GET.get("page") or 1
    try:
        page_obj = paginator.page(page_number)
    except EmptyPage:
        page_obj = paginator.page(paginator.num_pages)

    ctx = {
        "proyectos": page_obj,
        "prev_page": page_obj.previous_page_number() if page_obj.has_previous() else None,
        "next_page": page_obj.next_page_number() if page_obj.has_next() else None,
        "type_choices": Project._meta.get_field("type").choices,
        "q": q, "t": t, "e": e,
    }
    return render(request, "projectMain.html", ctx)


@login_required(login_url='log')
def projectDetail(request, pk):
    p = get_object_or_404(Project, pk=pk)
    return render(request, "projectDetail.html", {"p": p})


@login_required(login_url='log')
def projectCreate(request):
    if request.method == "POST":
        form = ProjectForm(request.POST, request.FILES)
        if form.is_valid():
            p = form.save(commit=False)
            p.usuario = request.user
            p.estado = "PL"
            p.save()
            messages.success(request, "¡Proyecto creado correctamente!")
            return redirect("projectMain")
    else:
        form = ProjectForm()
    return render(request, "projectForm.html", {"form": form})


@login_required(login_url='log')
def projectUpdate(request, pk):
    p = get_object_or_404(Project, pk=pk)
    old_file = p.imagen  # para limpiar si suben otro

    if request.method == "POST":
        form = ProjectForm(request.POST, request.FILES, instance=p)
        if form.is_valid():
            obj = form.save(commit=False)

            # estado desde el POST
            estado_post = request.POST.get("estado")
            if estado_post in dict(Project.ESTADO_CHOICES):
                obj.estado = estado_post

            obj.save()
            form.save_m2m()

            # si subieron imagen nueva, borro la anterior
            if old_file and request.FILES.get("imagen"):
                try:
                    if old_file.storage.exists(old_file.name) and old_file.name != obj.imagen.name:
                        old_file.storage.delete(old_file.name)
                except Exception:
                    pass

            messages.success(request, "¡Proyecto actualizado!")
            return redirect("projectMain")
    else:
        form = ProjectForm(instance=p)

    return render(request, "projectForm.html", {"form": form, "p": p})


@login_required
def projectDelete(request, pk):
    p = get_object_or_404(Project, pk=pk)
    if request.method == "POST":
        # Nota: si usas placeholder por defecto, no lo borres
        if p.imagen and p.imagen.name and p.imagen.name != "imgProjects/placeholder.jpg":
            try:
                p.imagen.delete(save=False)
            except Exception:
                pass
        p.delete()
        messages.success(request, "Proyecto eliminado.")
        return redirect("projectMain")
    return render(request, "projectConfirmDelete.html", {"p": p})


@login_required
def projectDetailList(request):
    qs = Project.objects.select_related("usuario", "tecnico").order_by("-created_at")

    q = (request.GET.get("q") or "").strip()
    t = (request.GET.get("type") or "").strip()
    e = (request.GET.get("estado") or "").strip()

    if q:
        qs = qs.filter(Q(nombre__icontains=q) | Q(cliente__icontains=q))
    if t:
        qs = qs.filter(type=t)
    if e:
        qs = qs.filter(estado=e)

    paginator = Paginator(qs, 7)
    page_number = request.GET.get("page") or 1
    try:
        page_obj = paginator.page(page_number)
    except EmptyPage:
        page_obj = paginator.page(paginator.num_pages)

    type_choices = Project._meta.get_field("type").choices

    return render(
        request,
        "projectDetailList.html",
        {"proyectos": page_obj, "type_choices": type_choices},
    )
