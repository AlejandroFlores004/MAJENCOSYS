from django.shortcuts import render
from .models import Project
from django.shortcuts import render, get_object_or_404

# Create your views here.
def projectMain(request): 
    proyectos = (
        Project.objects
        .select_related("usuario","tecnico")  #evita queries extra por FK
        .order_by("-id")   #ultimos creados van primero
    )
    return render(request, 'projectMain.html', { #Envia los datos al template
        "proyectos": proyectos
    }) 

def projectDetail(request, pk):
    p = get_object_or_404(Project, pk=pk)
    return render(request, "projectDetail.html", {"p": p}) 