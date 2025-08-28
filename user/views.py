from django.shortcuts import render,redirect
from django.contrib.auth.models import User,Group
from .forms import userForm
from django.contrib import messages

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
            messages.success(request, '!El usuario se guardo exitosamente')
            return redirect('usuariosMain')
    else:
        form = userForm()

    object = {
        "form" : form,
    }
    return render(request, 'usuarioForm.html', object)