# project/views.py
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, get_object_or_404, redirect
from django.core.paginator import Paginator, EmptyPage
from django.contrib import messages
from django.db.models import Q
from .models import Project, ArchivoTecnico
from .forms import ProjectForm, ArchivoTecnicoUploadForm, ArchivoTecnicoFilterForm
from datetime import datetime, time                                 # Permite búsquedas OR en filtros (Q objects).
from django.http import HttpRequest, HttpResponse, FileResponse, Http404                   # Respuestas de archivo y errores 404.
from django.shortcuts import get_object_or_404, redirect, render  # Atajos de vistas comunes.
from django.utils import timezone

@login_required(login_url='log')
def projectMain(request):
    qs = Project.objects.select_related("usuario", "tecnico").order_by("-created_at")

    q = (request.GET.get("q") or "").strip()
    t = (request.GET.get("type") or "").strip()
    e = (request.GET.get("estado") or "").strip()

    if q:
        qs = qs.filter(Q(nombre__icontains=q) | Q(cliente__icontains=q))
    if t:
        qs = qs.filter(type=t)
    if e:
        qs = qs.filter(estado=e)

    paginator = Paginator(qs, 7)  # 7 por página
    page_number = request.GET.get("page") or 1
    try:
        page_obj = paginator.page(page_number)
    except EmptyPage:
        page_obj = paginator.page(paginator.num_pages)

    ctx = {
        "proyectos": page_obj,
        "prev_page": page_obj.previous_page_number() if page_obj.has_previous() else None,
        "next_page": page_obj.next_page_number() if page_obj.has_next() else None,
        "type_choices": Project._meta.get_field("type").choices,
        "q": q, "t": t, "e": e,
    }
    return render(request, "projectMain.html", ctx)


@login_required(login_url='log')
def projectDetail(request, pk):
    p = get_object_or_404(Project, pk=pk)
    ultimos_archivos = p.archivos.all()[:5]   # ya viene ordenado por Meta.ordering
    total_archivos = p.archivos.count()
    return render(
        request,
        "projectDetail.html",
        {"p": p, "ultimos_archivos": ultimos_archivos, "total_archivos": total_archivos},
    )


@login_required(login_url='log')
def projectCreate(request):
    if request.method == "POST":
        form = ProjectForm(request.POST, request.FILES)
        if form.is_valid():
            p = form.save(commit=False)
            p.usuario = request.user
            p.estado = "PL"
            p.save()
            messages.success(request, "¡Proyecto creado correctamente!")
            return redirect("projectMain")
    else:
        form = ProjectForm()
    return render(request, "projectForm.html", {"form": form})


@login_required(login_url='log')
def projectUpdate(request, pk):
    p = get_object_or_404(Project, pk=pk)
    old_file = p.imagen  # para limpiar si suben otro

    if request.method == "POST":
        form = ProjectForm(request.POST, request.FILES, instance=p)
        if form.is_valid():
            obj = form.save(commit=False)

            # estado desde el POST
            estado_post = request.POST.get("estado")
            if estado_post in dict(Project.ESTADO_CHOICES):
                obj.estado = estado_post

            obj.save()
            form.save_m2m()

            # si subieron imagen nueva, borro la anterior
            if old_file and request.FILES.get("imagen"):
                try:
                    if old_file.storage.exists(old_file.name) and old_file.name != obj.imagen.name:
                        old_file.storage.delete(old_file.name)
                except Exception:
                    pass

            messages.success(request, "¡Proyecto actualizado!")
            return redirect("projectMain")
    else:
        form = ProjectForm(instance=p)

    return render(request, "projectForm.html", {"form": form, "p": p})


@login_required
def projectDelete(request, pk):
    p = get_object_or_404(Project, pk=pk)
    if request.method == "POST":
        # Nota: si usas placeholder por defecto, no lo borres
        if p.imagen and p.imagen.name and p.imagen.name != "imgProjects/placeholder.jpg":
            try:
                p.imagen.delete(save=False)
            except Exception:
                pass
        p.delete()
        messages.success(request, "Proyecto eliminado.")
        return redirect("projectMain")
    return render(request, "projectConfirmDelete.html", {"p": p})


@login_required
def projectDetailList(request):
    qs = Project.objects.select_related("usuario", "tecnico").order_by("-created_at")

    q = (request.GET.get("q") or "").strip()
    t = (request.GET.get("type") or "").strip()
    e = (request.GET.get("estado") or "").strip()

    if q:
        qs = qs.filter(Q(nombre__icontains=q) | Q(cliente__icontains=q))
    if t:
        qs = qs.filter(type=t)
    if e:
        qs = qs.filter(estado=e)

    paginator = Paginator(qs, 7)
    page_number = request.GET.get("page") or 1
    try:
        page_obj = paginator.page(page_number)
    except EmptyPage:
        page_obj = paginator.page(paginator.num_pages)

    type_choices = Project._meta.get_field("type").choices

    return render(
        request,
        "projectDetailList.html",
        {"proyectos": page_obj, "type_choices": type_choices},
    )


#CRUD de Carga de Archivos Tecnicos

def _clasifica_tipo_archivo(nombre: str, mime: str | None) -> str:
    n = (nombre or "").lower()
    m = (mime or "").lower()
    if "image/" in m or n.endswith((".png", ".jpg", ".jpeg", ".webp")):
        return "img"
    if n.endswith(".pdf") or m == "application/pdf":
        return "pdf"
    if n.endswith((".doc", ".docx", ".xls", ".xlsx", ".ppt", ".pptx")):
        return "doc"
    if n.endswith((".dwg", ".dxf")):
        return "dwg"
    if "video/" in m or n.endswith((".mp4", ".mov", ".mkv", ".avi")):
        return "video"
    if n.endswith(".bak"):
        return "bak"
    return "otros"

# -------------------- LISTAR + SUBIR (múltiple) ------------------------------
@login_required
def project_file_list_create(request: HttpRequest, pk: int) -> HttpResponse:
    project = get_object_or_404(Project, pk=pk)

    # POST: subida múltiple
    if request.method == "POST" and request.POST.get("__action") == "upload":
        upload_form = ArchivoTecnicoUploadForm(request.POST, request.FILES)
        filter_form = ArchivoTecnicoFilterForm(request.GET or None, user=request.user)
        if upload_form.is_valid():
            files = request.FILES.getlist("archivos")           # lista real
            descripcion = upload_form.cleaned_data.get("descripcion") or ""
            creados = 0
            for f in files:
                ArchivoTecnico.objects.create(
                    project=project,
                    archivo=f,                                   # usa upload_to => carpeta por proyecto
                    nombre_original=f.name,
                    tamano_bytes=int(getattr(f, "size", 0) or 0),
                    mime_type=getattr(f, "content_type", "") or (mimetypes.guess_type(f.name)[0] or ""),
                    subido_por=request.user,
                    descripcion=descripcion,
                    subido_en=timezone.now(),
                )
                creados += 1
            messages.success(request, f"Se subieron {creados} archivo(s).")
            return redirect("projectFiles", project.id)
        # si no es válido, continúa abajo y muestra errores junto a la lista
    else:
        upload_form = ArchivoTecnicoUploadForm()
        filter_form = ArchivoTecnicoFilterForm(request.GET or None, user=request.user)

    # GET: construir queryset con filtros
    files_qs = ArchivoTecnico.objects.filter(project=project).order_by("-subido_en")

    if filter_form.is_valid():
        q = filter_form.cleaned_data.get("q") or ""
        tipo = filter_form.cleaned_data.get("tipo") or ""
        usuario = filter_form.cleaned_data.get("usuario") or ""
        f1 = filter_form.cleaned_data.get("fecha_desde")
        f2 = filter_form.cleaned_data.get("fecha_hasta")

        if q:
            files_qs = files_qs.filter(Q(nombre_original__icontains=q) | Q(descripcion__icontains=q))
        if usuario:
            files_qs = files_qs.filter(subido_por_id=usuario)
        if f1:
            files_qs = files_qs.filter(subido_en__date__gte=f1)
        if f2:
            files_qs = files_qs.filter(subido_en__date__lte=f2)
        if tipo:
            ids = [
                f.id for f in files_qs.only("id", "nombre_original", "mime_type")
                if _clasifica_tipo_archivo(f.nombre_original, f.mime_type) == tipo
            ]
            files_qs = files_qs.filter(id__in=ids)

    ctx = {
        "project": project,
        "upload_form": upload_form,
        "filter_form": filter_form,
        "files": files_qs,
    }
    return render(request, "projectArchivosTecnicos.html", ctx)

# --------------------------- DESCARGAR ----------------------------------------
@login_required
def project_file_download(request: HttpRequest, pk: int, file_id: int) -> HttpResponse:
    f = get_object_or_404(ArchivoTecnico, pk=file_id, project_id=pk)
    if not f.archivo:
        raise Http404("Archivo no disponible.")
    return FileResponse(f.archivo.open("rb"), as_attachment=True, filename=f.nombre_original)

# ---------------------------- ELIMINAR ----------------------------------------
@login_required
def project_file_delete(request: HttpRequest, pk: int, file_id: int) -> HttpResponse:
    project = get_object_or_404(Project, pk=pk)
    f = get_object_or_404(ArchivoTecnico, pk=file_id, project=project)

    if request.method == "POST":
        # borra el archivo físico si existe
        try:
            if f.archivo and default_storage.exists(f.archivo.name):
                default_storage.delete(f.archivo.name)
        except Exception:
            pass
        # borra el registro
        f.delete()
        messages.success(request, "Archivo eliminado correctamente.")
        return redirect("projectFiles", project.id)

    # GET -> confirma
    return render(request, "projectConfirmDeleteAT.html", {"project": project, "f": f})