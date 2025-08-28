from django.shortcuts import render
from django.contrib.auth.models import User,Group
from .forms import userForm

# Create your views here.
def userMain(request):
    users = User.objects.all()
    groups = Group.objects.all()

    objects = {
        "usuarios" : users,
        "grupos" : groups
    }
    return render(request,'usuarioMain.html',objects)


def userFormView(request):
    if request.method == 'POST':
        form = userForm(request.POST)
        if form.is_valid():
            form.save()
    else:
        form = userForm()

    object = {
        "form" : form,
    }
    return render(request, 'usuarioForm.html', object)