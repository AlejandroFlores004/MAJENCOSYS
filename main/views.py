import os
import subprocess
from datetime import datetime
from django.conf import settings
from django.http import HttpResponse, FileResponse
from django.shortcuts import render,redirect
from django.contrib.auth import login,logout, authenticate
from django.contrib import messages
from .forms import UserRegistrationForm
from django.contrib.auth.decorators import login_required
from django.urls import reverse
from project.models import Project
from django.core.paginator import Paginator
from django.db.models import Count


# Create your views here.
# Pagina inicial
def startpage(request):
    return render(request, 'starPageClientes.html')

# Dashboard de area de trabajo
@login_required(login_url='log')
def dashboard(request):
    # Get all projects
    projects_list = Project.objects.all().order_by('-created_at')  

    # Pagination
    paginator = Paginator(projects_list, 4)
    page_number = request.GET.get('page')
    projects = paginator.get_page(page_number)

    # Count projects by type
    project_types = (
        Project.objects
        .values('type')  # Group by 'type'
        .annotate(total=Count('id'))  # Count projects
        .order_by('type')
    )

    # Convert codes to human-readable names
    type_choices_dict = dict(Project.TYPE_CHOICES)
    for pt in project_types:
        pt['type_name'] = type_choices_dict.get(pt['type'], pt['type'])

    context = {
        "projects": projects,
        "project_types": project_types,
    }
    return render(request, 'dashboard.html', context)

# Login de usuarios
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
            messages.success(request, 'Has iniciado sesión correctamente.')
            return redirect('dashboard')
            
        else:
            messages.error(request, 'Credenciales inválidas. Inténtalo de nuevo.')
    objects = {
        "form": UserRegistrationForm(),
        "message": message
    }
    return render(request, 'login.html', objects)

# Información general de usuario en sesión
@login_required(login_url='log')
def userInfo(request):
   objects = {
       "usuario":request.user
   }
   return render(request, 'usuarioSesionInfo.html',objects) 

@login_required(login_url='log')
def logoutUser(request):
    if request.method == 'POST':
        logout(request)
        messages.success(request, "Has cerrado sesión correctamente.")
        return redirect('log')
    return render(request, 'logout.html')

# ------ Herramientas de base de datos (Backup y Restore) ------
def admin_required(view_func):
    def _wrapped_view(request, *args, **kwargs):
        # Step 1: Check if the user is logged in
        if not request.user.is_authenticated:
            return redirect(f"{reverse('log')}?next={request.path}")

        # Step 2: Check if user is superuser
        if not request.user.is_superuser:
            messages.warning(request, "No tienes las credenciales necesarias para acceder a esta sección.")
            return redirect('dashboard')  # Redirect to dashboard

        # Step 3: Allow access
        return view_func(request, *args, **kwargs)
    
    return _wrapped_view

@login_required(login_url='log')
@admin_required
def database_tools(request):
    db_settings = settings.DATABASES['default']

    if request.method == "POST" and "restore" in request.POST:
        # ---- RESTORE ----
        backup_file = request.FILES.get("backup_file")
        if not backup_file:
            messages.error(request, "Por favor selecciona un archivo de respaldo para subir.")
            return redirect("database_tools")

        temp_path = os.path.join(settings.BASE_DIR, "temp_restore.sql")

        # Save uploaded file temporarily
        with open(temp_path, "wb+") as destination:
            for chunk in backup_file.chunks():
                destination.write(chunk)

        # Build command WITHOUT including password directly
        command = [
            "mysql",
            "-u", db_settings['USER'],
            "-h", db_settings.get('HOST', 'localhost'),
            "-P", str(db_settings.get('PORT', 3306)),
            db_settings['NAME']
        ]

        # Securely pass password through environment variable
        env = os.environ.copy()
        env["MYSQL_PWD"] = db_settings['PASSWORD']

        try:
            # Run mysql restore with file input
            with open(temp_path, "rb") as f:
                subprocess.run(
                    command,
                    stdin=f,
                    env=env,  # pass password securely
                    check=True
                )

            os.remove(temp_path)  # Clean up
            messages.success(request, "¡Base de datos restaurada con éxito!")

        except subprocess.CalledProcessError as e:
            error_msg = e.stderr.decode() if e.stderr else str(e)
            messages.error(request, f"Error al restaurar la base de datos: {error_msg}")

        return redirect("database_tools")
    
    return render(request, "backUpTools.html")


def download_backup(request):
    db_settings = settings.DATABASES['default']

    # Create a copy of current environment and add MYSQL_PWD
    env = os.environ.copy()
    env["MYSQL_PWD"] = db_settings['PASSWORD']

    # Build the mysqldump command without the `-pPASSWORD`
    command = [
        "mysqldump",
        "-u", db_settings['USER'],
        "-h", db_settings.get('HOST', 'localhost'),
        "-P", str(db_settings.get('PORT', 3306)),
        db_settings['NAME']
    ]

    try:
        # Run mysqldump
        result = subprocess.run(
            command,
            env=env,  # pass the password securely
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            check=True
        )

        # Create filename with timestamp
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"backup_majencosys_{timestamp}.sql"

        # Return as downloadable file
        response = HttpResponse(result.stdout, content_type='application/sql')
        response['Content-Disposition'] = f'attachment; filename="{filename}"'
        return response

    except subprocess.CalledProcessError as e:
        error_msg = e.stderr.decode()
        print("Error generating backup:", error_msg)
        return HttpResponse(f"Backup failed: {error_msg}", status=500)
