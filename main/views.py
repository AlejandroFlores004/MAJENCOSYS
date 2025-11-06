import os
import subprocess
from datetime import datetime, timedelta, date

from django.conf import settings
from django.contrib import messages
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.db.models import Count, Prefetch, Q
from django.http import HttpResponse, FileResponse, JsonResponse
from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse

from .forms import UserRegistrationForm
from project.models import Project
from activity.models import Activity, Header
from catalog.models import (
    Material,
    ManoObra,
    Equipo,
    Herramienta,
    Riesgo,
    Calidad,
    Ambiental,
    Hidrologica,
)
from schedule.models import Schedule



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

@login_required(login_url='log')
def dashboardProject(request, pk):
    project = get_object_or_404(Project, pk=pk)

    # parámetros GET
    page = request.GET.get('page', 1)
    per_page = int(request.GET.get('per_page', 5))  # ajusta default

    # queryset con prefetch
    qs = (
        Activity.objects
        .filter(project=project)
        .order_by('-id')  # o 'name' / '-created_at' según prefieras
        .prefetch_related(
            Prefetch(
                'header_activity',  # usa tu related_name real si es distinto
                queryset=Header.objects.only('id', 'name', 'content', 'activity_id').order_by('id')
            )
        )
    )

    paginator = Paginator(qs, per_page)
    try:
        activities_page = paginator.page(page)
    except PageNotAnInteger:
        activities_page = paginator.page(1)
    except EmptyPage:
        activities_page = paginator.page(paginator.num_pages)

    countMaterial = Material.objects.filter(project=project).count()
    countEquipo = Equipo.objects.filter(project=project).count()
    countManoObra = ManoObra.objects.filter(project=project).count()
    countHerramienta = Herramienta.objects.filter(project=project).count()
    countRiesgo = Riesgo.objects.filter(project=project).count()
    countCalidad = Calidad.objects.filter(project=project).count()
    countAmbiental = Ambiental.objects.filter(project=project).count()
    countHidrologica = Hidrologica.objects.filter(project=project).count()

    context = {
        "project": project,
        "activities_page": activities_page,
        "paginator_activities": paginator,
        "is_paginated_activities": paginator.num_pages > 1,
        "per_page_activities": per_page,
        "quiantyMaterial": countMaterial,
        "quiantyEquipo": countEquipo,
        "quiantyManoObra": countManoObra,
        "quiantyHerramienta": countHerramienta,
        "quiantyRiesgo": countRiesgo,
        "quiantyCalidad": countCalidad,
        "quiantyAmbiental": countAmbiental,
        "quiantyHidrologica": countHidrologica,
    }
    return render(request, 'dashboardProject.html', context)


def _parse_date(value: str) -> date | None:
    try:
        return date.fromisoformat(value[:10])  # 'YYYY-MM-DD...' -> date
    except Exception:
        return None

def _status_color(code: str) -> str:
    # P=Planeado, E=Ejecutando, F=Finalizado
    return {
        'P': '#6c757d',  # gris
        'E': '#ffc107',  # amarillo
        'F': '#198754',  # verde
    }.get(code, '#0d6efd')  # fallback azul

@login_required(login_url='log')
def project_schedule_events(request, pk):
    project = get_object_or_404(Project, pk=pk)

    # Rangos que envía FullCalendar (opcional, pero recomendado)
    start_qs = _parse_date(request.GET.get('start', ''))
    end_qs   = _parse_date(request.GET.get('end', ''))

    qs = (
        Schedule.objects
        .filter(activity__project=project)
        .select_related('activity')
        .only('id', 'start_date', 'end_date', 'status', 'activity_id')
        .order_by('start_date', 'id')
    )

    # Filtrado por rango: traer cualquier schedule que toque la ventana
    if start_qs and end_qs:
        qs = qs.filter(
            Q(start_date__lte=end_qs) & Q(end_date__gte=start_qs)
        )

    events = []
    for s in qs:
        # Como son DateField y se mostrarán "allDay", FullCalendar espera end EXCLUSIVO.
        # Sumamos +1 día para que el rango sea inclusivo en UI.
        end_exclusive = s.end_date + timedelta(days=1)

        # (Opcional) link a algún detalle de actividad o cronograma
        # Ajusta a tu URL real (ej. 'memoryMananer' ya lo vi en tu proyecto)
        try:
            detail_url = reverse('memoryMananer', args=[project.pk, s.activity.pk])
        except Exception:
            detail_url = '#'

        color = _status_color(s.status)

        events.append({
            "id": s.id,
            "title": s.activity.name,  # Título del evento (nota en el calendario)
            "start": s.start_date.isoformat(),
            "end": end_exclusive.isoformat(),
            "allDay": True,
            "backgroundColor": color,
            "borderColor": color,
            "extendedProps": {
                "status": s.get_status_display(),
                "author": "",  # si luego quieres incluir usuario creador, etc.
                "description": f"{s.get_status_display()} · {s.start_date} → {s.end_date}",
                "url": detail_url,
            },
        })

    return JsonResponse(events, safe=False)
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
