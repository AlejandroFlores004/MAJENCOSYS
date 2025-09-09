from django.shortcuts import render,redirect, get_object_or_404
from django.contrib.auth.models import User,Group
from .forms import userForm, UserUpdateForm,UserUpdatePasswordForm
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator, EmptyPage
from django.db.models import Q

# Create your views here.
@login_required(login_url='log')
def userMain(request):
    users = User.objects.all()
    groups = Group.objects.all()

    objects = {
        "usuarios" : users,
        "grupos" : groups
    }
    
    return render(request,'usuarioMain.html',objects)

@login_required(login_url='log')
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

@login_required(login_url='log')
def userDetails(request):
    qs = User.objects.select_related().order_by("-date_joined")
    groups = Group.objects.all()

    # Get filter params
    q = (request.GET.get("q") or "").strip()
    g = (request.GET.get("group") or "").strip()
    s = (request.GET.get("status") or "").strip()

    # Apply filters
    if q:
        qs = qs.filter(
            Q(username__icontains=q) |
            Q(first_name__icontains=q) |
            Q(last_name__icontains=q) |
            Q(email__icontains=q)
        )
    if g:
        qs = qs.filter(groups__id=g)
    if s:
        if s == "active":
            qs = qs.filter(is_active=True)
        elif s == "inactive":
            qs = qs.filter(is_active=False)

    # Pagination
    paginator = Paginator(qs, 10)  # 10 users per page
    page_number = request.GET.get("page") or 1
    try:
        page_obj = paginator.page(page_number)
    except EmptyPage:
        page_obj = paginator.page(paginator.num_pages)

    context = {
        "usuarios": page_obj,
        "grupos": groups,
        "q": q,
        "g": g,
        "s": s,
    }
    return render(request, 'usuariosDetails.html', context)

@login_required(login_url='log')
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

@login_required(login_url='log')
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

def userEditStatus(request, pk):
    user_obj = get_object_or_404(User, pk=pk)

    if request.method == 'POST':
        user_obj.is_active = not user_obj.is_active
        user_obj.save()
        messages.success(request, '¡Estado de usuario actualizado correctamente!')
        return redirect('usuarioDetails')

    object = {
        "usuario": user_obj,
    }
    return render(request, 'usuarioCambiarEstado.html', object)

@login_required(login_url='log')
def userDelete(request, pk):
    user_obj = get_object_or_404(User, pk=pk)

    if request.method == 'POST':
        user_obj.delete()
        messages.success(request, '¡Usuario eliminado correctamente!')
        return redirect('usuarioDetails')

    object = {
        "usuario": user_obj,
    }
    return render(request, 'usuarioDelete.html', object)
