from django.shortcuts import render
from project.models import Project
from django.shortcuts import get_object_or_404
# Create your views here.
def mainActivityCrmv(request, pk):
    project = get_object_or_404(Project, pk=pk)
    objects = {
        'project': project,
    }
    return render(request, 'mainActivityCmrv.html', objects)
