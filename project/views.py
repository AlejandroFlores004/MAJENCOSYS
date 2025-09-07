from django.shortcuts import render, redirect, get_object_or_404
from django.core.paginator import Paginator
from django.contrib import messages

from .models import Project
from .forms import ProjectForm


# Lista + paginación
def projectMain(request):
    qs = Project.objects.select_related("usuario", "tecnico").order_by("-created_at")
    page = Paginator(qs, 10).get_page(request.GET.get("page"))  # get_page evita errores si ?page=0 o inválida
    return render(request, "projectMain.html", {"proyectos": page})


# Detalle
def projectDetail(request, pk):
    p = get_object_or_404(Project, pk=pk)
    return render(request, "projectDetail.html", {"p": p})


# Crear
def projectCreate(request):
    if request.method == "POST":
        form = ProjectForm(request.POST, request.FILES)
        if form.is_valid():
            p = form.save(commit=False)
            # Debe existir un usuario autenticado
            p.usuario = request.user
            p.estado = "PL"  # Planeación por defecto al crear
            if 'delete_imagen' in request.POST:
                p.imagen = None
            p.save()
            messages.success(request, "¡Proyecto creado correctamente!")
            return redirect("projectMain")
        else:
            messages.error(request, "Revisa los errores del formulario.")
    else:
        form = ProjectForm()
    return render(request, "projectForm.html", {"form": form})


# Editar
def projectUpdate(request, pk):
    p = get_object_or_404(Project, pk=pk)
    if request.method == "POST":
        form = ProjectForm(request.POST, request.FILES, instance=p)
        if form.is_valid():
            p = form.save(commit=False)
            # Estado viene de un <select> manual cuando EDITAS
            estado = (request.POST.get("estado") or "").strip()
            if estado in ("PL", "P", "C"):
                p.estado = estado
            if 'delete_imagen' in request.POST:
                if p.imagen:
                    p.imagen.delete(save=False)
                p.imagen = None
            p.save()
            messages.success(request, "¡Proyecto actualizado correctamente!")
            return redirect("projectMain")
        else:
            messages.error(request, "Formulario inválido. Corrige los errores.")
    else:
        form = ProjectForm(instance=p)
    return render(request, "projectForm.html", {"form": form, "p": p})


# Eliminar
def projectDelete(request, pk):
    p = get_object_or_404(Project, pk=pk)
    if request.method == "POST":
        p.delete()
        messages.success(request, "Proyecto eliminado.")
        return redirect("projectMain")
    return render(request, "projectConfirmDelete.html", {"p": p})


# Tabla de detalles
def projectDetailList(request):
    proyectos = Project.objects.select_related("usuario", "tecnico").order_by("-created_at")
    return render(request, "projectDetailList.html", {"proyectos": proyectos})
