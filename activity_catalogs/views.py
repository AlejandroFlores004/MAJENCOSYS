from json import tool
from django.shortcuts import render,redirect, get_object_or_404
from .models import Project, Tool, Labour, Material
from .forms import ToolForm, LabourForm, MaterialForm
from django.http import HttpResponse



# Create your views here.

def homeCatalogs(request, pk):
    project = Project.objects.get(id=pk)
    return render(request, 'homeCatalogs.html', {'project': project})

def formTools(request, pk):
    project = get_object_or_404(Project, pk=pk)
    if request.method == "POST":
        form = ToolForm(request.POST)
        if form.is_valid():
            tool = form.save(commit=False)
            tool.project = project
            tool.save()
            # Aquí puedes redirigir a otra página o mostrar un mensaje de éxito
            if request.GET.get("popup", None) == "1":
                return HttpResponse(f"""
                <script>
                  opener.closePopupAndAddTool("{tool.pk}", "{tool.name} - ${tool.dayCost}");
                  window.close();
                </script>
                """)

            # Si no es popup, comportamiento normal
            return redirect("activity_catalogs_home", pk=project.id)
        
    else:
        form = ToolForm()
    return render(request, 'toolsForm.html', {'form': form, 'project': project})


def editTool(request, pk, tool_id):
    project = get_object_or_404(Project, pk=pk)
    tool = get_object_or_404(Tool, pk=tool_id, project=project)

    if request.method == "POST":
        form = ToolForm(request.POST, instance=tool)
        if form.is_valid():
            tool = form.save()

            if request.GET.get("popup", None) == "1":
                return HttpResponse(f"""
                <script>
                  opener.updateToolInSelect("{tool.pk}", "{tool.name} - ${tool.dayCost}");
                  window.close();
                </script>
                """)
            return redirect("activity_catalogs_home", pk=project.id)
    else:
        form = ToolForm(instance=tool)

    return render(request, "toolsForm.html", {"form": form, "project": project, "tool": tool})


def formLabour(request, pk):
    project = get_object_or_404(Project, pk=pk)
    if request.method == "POST":
        form = LabourForm(request.POST)
        if form.is_valid():
            labour = form.save(commit=False)
            labour.project = project
            labour.save()
            # Aquí puedes redirigir a otra página o mostrar un mensaje de éxito
            if request.GET.get("popup", None) == "1":
                return HttpResponse(f"""
                <script>
                  opener.closePopupAndAddLabour("{labour.pk}", "{labour.name} - ${labour.price} ({labour.project.nombre})");
                  window.close();
                </script>
                """)

            # Si no es popup, comportamiento normal
            return redirect("activity_catalogs_home", pk=project.id)
        
    else:
        form = LabourForm()
    return render(request, 'labourForm.html', {'form': form, 'project': project})

def editLabour(request, pk, labour_id):
    project = get_object_or_404(Project, pk=pk)
    labour = get_object_or_404(Labour, pk=labour_id, project=project)

    if request.method == "POST":
        form = LabourForm(request.POST, instance=labour)
        if form.is_valid():
            labour = form.save()

            if request.GET.get("popup", None) == "1":
                return HttpResponse(f"""
                <script>
                  opener.updateLabourInSelect("{labour.pk}", "{labour.description} - ${labour.price}");
                  window.close();
                </script>
                """)
            return redirect("activity_catalogs_home", pk=project.id)
    else:
        form = LabourForm(instance=labour)

    return render(request, "labourForm.html", {"form": form, "project": project, "labour": labour})

def formMaterial(request, pk):
    project = get_object_or_404(Project, pk=pk)
    if request.method == "POST":
        form = MaterialForm(request.POST)
        if form.is_valid():
            material = form.save(commit=False)
            material.project = project
            material.save()
            # Aquí puedes redirigir a otra página o mostrar un mensaje de éxito
            if request.GET.get("popup", None) == "1":
                return HttpResponse(f"""
                <script>
                  opener.closePopupAndAddMaterial("{material.pk}", "{material.name} - ${material.price}");
                  window.close();
                </script>
                """)

            # Si no es popup, comportamiento normal
            return redirect("activity_catalogs_home", pk=project.id)

    else:
        form = MaterialForm()
    return render(request, 'materialForm.html', {'form': form, 'project': project})

def editMaterial(request, pk, material_id):
    project = get_object_or_404(Project, pk=pk)
    material = get_object_or_404(Material, pk=material_id, project=project)

    if request.method == "POST":
        form = MaterialForm(request.POST, instance=material)
        if form.is_valid():
            material = form.save()

            if request.GET.get("popup", None) == "1":
                return HttpResponse(f"""
                <script>
                  opener.updateMaterialInSelect("{material.pk}", "{material.name} - ${material.price}");
                  window.close();
                </script>
                """)
            return redirect("activity_catalogs_home", pk=project.id)
    else:
        form = MaterialForm(instance=material)
    return render(request, "materialForm.html", {"form": form, "project": project, "material": material})