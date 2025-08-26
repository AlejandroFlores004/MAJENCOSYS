from django.shortcuts import render
from django.contrib.auth.models import User,Group

# Create your views here.
def userMain(request):
    users = User.objects.all()
    groups = Group.objects.all()

    objects = {
        "usuarios" : users,
        "grupos" : groups
    }
    return render(request,'usuarioMain.html',objects)