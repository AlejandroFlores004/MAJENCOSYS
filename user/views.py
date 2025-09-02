from django.shortcuts import render,redirect, get_object_or_404
from django.contrib.auth.models import User,Group
from .forms import userForm, UserUpdateForm,UserUpdatePasswordForm
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

def userDetails(request):
    users = User.objects.filter(is_active=True)
    groups = Group.objects.all()

    objects = {
        "usuarios" : users,
        "grupos" : groups
    }
    return render(request, 'usuariosDetails.html', objects)

def userEdit(request, pk):
    user_obj = get_object_or_404(User, pk=pk)

    if request.method == 'POST':
        form = UserUpdateForm(request.POST, instance=user_obj)
        if form.is_valid():
            form.save()
            messages.success(request, '¡Usuario actualizado correctamente!')
            return redirect('usuarioDetails')  # vuelve a la tabla
    else:
        form = UserUpdateForm(instance=user_obj)

    objects = {
        "form": form,
        "usuario": user_obj
    }

    return render(request, 'usuarioEdit.html', objects)


def userEditPassword(request, pk):
    user_obj = get_object_or_404(User, pk=pk)

    if request.method == 'POST':
        form = UserUpdatePasswordForm(user=user_obj, data=request.POST)
        if form.is_valid():
            form.save()  # hashes and sets the new password
            messages.success(request, '¡Contraseña actualizada correctamente!')
            return redirect('usuarioDetails')  # adjust to your detail URL
    else:
        form = UserUpdatePasswordForm(user=user_obj)

    context = {
        "form": form,
        "usuario": user_obj,
    }
    return render(request, 'usuarioEditPassword.html', context)
