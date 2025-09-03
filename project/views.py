from django.shortcuts import render, redirect, get_object_or_404
from .models import Project
from .forms import ProjectForm


def projectMain(request):
    proyectos = (
        Project.objects
        .select_related("usuario", "tecnico")
        .order_by("-id")
    )
    return render(request, "projectMain.html", {"proyectos": proyectos})


def projectDetail(request, pk):
    p = get_object_or_404(Project, pk=pk)
    return render(request, "projectDetail.html", {"p": p})


def projectCreate(request):
    if request.method == "POST":
        form = ProjectForm(request.POST)
        if form.is_valid():
            p = form.save()
            return redirect("projectDetail", pk=p.pk)
    else:
        form = ProjectForm()
        if request.user.is_authenticated:
            form.fields["usuario"].initial = request.user

    # Respuesta común para GET y POST inválido
    return render(request, "projectForm.html", {"form": form})


def projectUpdate(request, pk):
    p = get_object_or_404(Project, pk=pk)

    if request.method == "POST":
        form = ProjectForm(request.POST, instance=p)
        if form.is_valid():
            p = form.save()
            return redirect("projectDetail", pk=p.pk)
    else:
        form = ProjectForm(instance=p)

    return render(request, "projectForm.html", {"form": form, "p": p})


def projectDelete(request, pk):
    p = get_object_or_404(Project, pk=pk)

    if request.method == "POST":
        p.delete()
        return redirect("projectMain")

    return render(request, "projectConfirmDelete.html", {"p": p})
