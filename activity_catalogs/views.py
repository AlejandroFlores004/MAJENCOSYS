from django.shortcuts import render,redirect, get_object_or_404
from .models import Project, Tool
from .forms import ToolForm
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
