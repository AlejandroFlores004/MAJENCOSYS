from django.shortcuts import render
from django.contrib.auth.models import User

# Create your views here.
def userMain(request):
    users = User.objects.all()
    objects = {
        "usuarios" : users
    }
    return render(request,'usuarioMain.html',objects)