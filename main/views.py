from django.shortcuts import render,redirect
from django.contrib.auth.models import User
from django.contrib.auth import login,logout, authenticate
from django.contrib import messages
from .forms import UserRegistrationForm

# Create your views here.
def startpage(request):
    return render(request, 'starPageClientes.html')


def dashboard(request):
    return render(request, 'dashboard.html')

def loginPage(request):
    message = ''
    if request.method == 'POST':
        user = authenticate(
            request,
            username=request.POST['username'],
            password=request.POST['password']
        )
        if user is not None:
            
            login(request, user)
            return redirect('dashboard')
            
        else:
            messages.warning(request, 'Credenciales inválidas. Inténtalo de nuevo.')
    objects = {
        "form": UserRegistrationForm(),
        "message": message
    }
    return render(request, 'login.html', objects)