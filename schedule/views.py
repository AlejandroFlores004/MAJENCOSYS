from django.shortcuts import render 
from django.shortcuts import get_object_or_404
from project.models import Project
from django.contrib.auth.decorators import login_required
# Create your views here.

@login_required(login_url='log')
def mainSchedule(request, pk):
    project = get_object_or_404(Project, pk=pk)
    context = {
        'project': project,
    }
    return render(request, 'mainSchedule.html', context)