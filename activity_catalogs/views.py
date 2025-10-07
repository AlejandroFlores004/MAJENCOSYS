from json import tool
from django.shortcuts import render,redirect, get_object_or_404
from .models import Project, Tool, Labour, Material, HeavyMachinery, QualityControl
from .forms import ToolForm, LabourForm, MaterialForm, HeavyMachineryForm, QualityControlForm
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


# views.py
from django.utils.html import escapejs
# ...

def editTool(request, pk, tool_id):
    project = get_object_or_404(Project, pk=pk)
    tool = get_object_or_404(Tool, pk=tool_id, project=project)

    if request.method == "POST":
        form = ToolForm(request.POST, instance=tool)
        if form.is_valid():
            tool = form.save()

            if request.GET.get("popup") == "1":
                label = f"{tool.name} - ${tool.dayCost}"
                safe_label = escapejs(label)
                return HttpResponse(f"""
                <script>
                  if (window.opener && !window.opener.closed) {{
                    window.opener.updateToolInSelect("{tool.pk}", "{safe_label}");
                  }}
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

            if request.GET.get("popup") == "1":
                label = f"{labour.name} - ${labour.price} ({labour.project.nombre})"
                safe_label = escapejs(label)
                return HttpResponse(f"""
                <script>
                  if (window.opener && !window.opener.closed) {{
                    window.opener.closePopupAndAddLabour("{labour.pk}", "{safe_label}");
                  }}
                  window.close();
                </script>
                """)
            return redirect("activity_catalogs_home", pk=project.id)
    else:
        form = LabourForm()
    return render(request, "labourForm.html", {"form": form, "project": project})

def editLabour(request, pk, labour_id):
    project = get_object_or_404(Project, pk=pk)
    labour = get_object_or_404(Labour, pk=labour_id, project=project)

    if request.method == "POST":
        form = LabourForm(request.POST, instance=labour)
        if form.is_valid():
            labour = form.save()

            if request.GET.get("popup") == "1":
                # usa el campo que quieras mostrar (name o description)
                label = f"{labour.name} - ${labour.price}"
                safe_label = escapejs(label)
                return HttpResponse(f"""
                <script>
                  if (window.opener && !window.opener.closed) {{
                    window.opener.updateLabourInSelect("{labour.pk}", "{safe_label}");
                  }}
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
            if request.GET.get("popup") == "1":
                label = f"{material.name} - ${material.price}"
                safe_label = escapejs(label)
                return HttpResponse(f"""
                <script>
                if (window.opener && !window.opener.closed) {{
                    window.opener.closePopupAndAddMaterial("{material.pk}", "{safe_label}");
                }}
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
            if request.GET.get("popup") == "1":
                label = f"{material.name} - ${material.price}"
                safe_label = escapejs(label)
                return HttpResponse(f"""
                <script>
                if (window.opener && !window.opener.closed) {{
                    window.opener.updateMaterialInSelect("{material.pk}", "{safe_label}");
                }}
                window.close();
                </script>
                """)
    else:
        form = MaterialForm(instance=material)
    return render(request, "materialForm.html", {"form": form, "project": project, "material": material})


def formHeavyMachinery(request, pk):
    project = get_object_or_404(Project, pk=pk)
    if request.method == "POST":
        form = HeavyMachineryForm(request.POST)
        if form.is_valid():
            machine = form.save(commit=False)
            machine.project = project
            machine.save()

            if request.GET.get("popup") == "1":
                label = f"{machine.name} ({machine.get_function_display()}) - ${machine.price}"
                safe_label = escapejs(label)
                return HttpResponse(f"""
                <script>
                  if (window.opener && !window.opener.closed) {{
                    window.opener.closePopupAndAddHeavyMachinery("{machine.pk}", "{safe_label}");
                  }}
                  window.close();
                </script>
                """)
            return redirect("activity_catalogs_home", pk=project.id)
    else:
        form = HeavyMachineryForm()

    return render(request, "heavyMachineryForm.html", {"form": form, "project": project})


def editHeavyMachinery(request, pk, machinery_id):
    project = get_object_or_404(Project, pk=pk)
    machine = get_object_or_404(HeavyMachinery, pk=machinery_id, project=project)

    if request.method == "POST":
        form = HeavyMachineryForm(request.POST, instance=machine)
        if form.is_valid():
            machine = form.save()

            if request.GET.get("popup") == "1":
                label = f"{machine.name} ({machine.get_function_display()}) - ${machine.price}"
                safe_label = escapejs(label)
                return HttpResponse(f"""
                <script>
                  if (window.opener && !window.opener.closed) {{
                    window.opener.updateHeavyMachineryInSelect("{machine.pk}", "{safe_label}");
                  }}
                  window.close();
                </script>
                """)
            return redirect("activity_catalogs_home", pk=project.id)
    else:
        form = HeavyMachineryForm(instance=machine)

    return render(
        request,
        "heavyMachineryForm.html",
        {"form": form, "project": project, "machine": machine}
    )


# =====================
# QUALITY CONTROL (CRUD)
# =====================
def formQualityControl(request, pk):
    project = get_object_or_404(Project, pk=pk)
    if request.method == "POST":
        form = QualityControlForm(request.POST)
        if form.is_valid():
            test = form.save(commit=False)
            test.project = project
            test.save()

            if request.GET.get("popup") == "1":
                label = f"{test.name} - {test.responsible.get_full_name() or test.responsible.username}"
                safe_label = escapejs(label)
                return HttpResponse(f"""
                <script>
                  if (window.opener && !window.opener.closed) {{
                    window.opener.closePopupAndAddQualityControl("{test.pk}", "{safe_label}");
                  }}
                  window.close();
                </script>
                """)
            return redirect("activity_catalogs_home", pk=project.id)
    else:
        form = QualityControlForm()

    return render(request, "qualityControlForm.html", {"form": form, "project": project})


def editQualityControl(request, pk, test_id):
    project = get_object_or_404(Project, pk=pk)
    test = get_object_or_404(QualityControl, pk=test_id, project=project)

    if request.method == "POST":
        form = QualityControlForm(request.POST, instance=test)
        if form.is_valid():
            test = form.save()

            if request.GET.get("popup") == "1":
                label = f"{test.name} - {test.responsible.get_full_name() or test.responsible.username}"
                safe_label = escapejs(label)
                return HttpResponse(f"""
                <script>
                  if (window.opener && !window.opener.closed) {{
                    window.opener.updateQualityControlInSelect("{test.pk}", "{safe_label}");
                  }}
                  window.close();
                </script>
                """)
            return redirect("activity_catalogs_home", pk=project.id)
    else:
        form = QualityControlForm(instance=test)

    return render(
        request,
        "qualityControlForm.html",
        {"form": form, "project": project, "test": test}
    )