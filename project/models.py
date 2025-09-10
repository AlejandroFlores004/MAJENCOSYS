from django.db import models
from django import forms
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from django.core.files.storage import default_storage
import os  # Módulo estándar para manejar rutas y nombres de archivo.
from uuid import uuid4  # Para generar identificadores únicos y evitar choques de nombres.
import mimetypes  # Para inferir el tipo MIME a partir del nombre del archivo.
from django.conf import settings  # Para referenciar el modelo de usuario configurado.
from django.utils import timezone  # Fechas/horas conscientes de zona horaria.
from django.utils.translation import gettext_lazy as _
import re

def validate_image_size(image):
    """Máximo 5 MB; si el archivo no existe en disco, no revienta."""
    if not image or not getattr(image, "name", None):
        return
    try:
        if image.size > 5 * 1024 * 1024:
            raise ValidationError("La imagen no debe superar 5 MB.")
    except (FileNotFoundError, OSError):
        # Si el path no existe (caso histórico), no romper validación del form
        return

def validate_image_extension(image):
    """Solo JPG/PNG/WEBP."""
    if not image or not getattr(image, "name", None):
        return
    ext = image.name.lower().rsplit(".", 1)[-1]
    if ext not in ("jpg", "jpeg", "png", "webp"):
        raise ValidationError("La imagen debe ser JPG, PNG o WEBP.")

class Project(models.Model):
    # Catálogos
    TIPO_ALCANTARILLADO = "AL"
    TIPO_OBRAS_MITIG = "OBM"
    TIPO_RED_VIAL = "CMV"      # Construcción y Mantenimiento de Red Vial
    TIPO_INFRA = "INF"

    TYPE_CHOICES = (
        (TIPO_ALCANTARILLADO, "Alcantarillado"),
        (TIPO_OBRAS_MITIG, "Obras de Mitigación"),
        (TIPO_RED_VIAL, "Construcción y Mantenimiento de Red Vial"),
        (TIPO_INFRA, "Infraestructura"),
    )

    ESTADO_PLAN = "PL"
    ESTADO_PROC = "P"
    ESTADO_COMP = "C"

    ESTADO_CHOICES = (
        (ESTADO_PLAN, "Planeación"),
        (ESTADO_PROC, "En Proceso"),
        (ESTADO_COMP, "Completado"),
    )

    # Campos
    nombre = models.CharField("Nombre del Proyecto", max_length=150)
    cliente = models.CharField("Nombre del Cliente", max_length=150)

    usuario = models.ForeignKey(
        User, on_delete=models.PROTECT, related_name="proyectos_creados",
        verbose_name="Usuario creador",
    )
    tecnico = models.ForeignKey(
        User, on_delete=models.PROTECT, related_name="proyectos_asignados",
        verbose_name="Técnico asignado",
    )

    type = models.CharField("Tipo de Proyecto", max_length=3, choices=TYPE_CHOICES)
    estado = models.CharField("Estado", max_length=2, choices=ESTADO_CHOICES, default=ESTADO_PLAN)

    imagen = models.ImageField(
    "Imagen Proyecto",
    upload_to="imgProjects/",
    blank=True,          # <— importante
    null=True,           # <— importante
    validators=[validate_image_size, validate_image_extension],
    )


    descripcion = models.TextField("Descripción", blank=False)

    created_at = models.DateTimeField("Fecha de Creación", auto_now_add=True)
    updated_at = models.DateTimeField("Última Actualización", auto_now=True)

    class Meta:
        ordering = ("-created_at",)
        verbose_name = "Proyecto"
        verbose_name_plural = "Proyectos"

    def __str__(self):
        return self.nombre

#Crud Carga de Archivos tecnicos
# ====================== Config para archivos técnicos ========================

def _allowed_exts():
    # Puedes sobreescribir en settings.ALLOWED_FILE_EXTS
    return getattr(
        settings, "ALLOWED_FILE_EXTS",
        ["pdf", "dwg", "docx", "xlsx", "mp4", "bak", "jpg", "jpeg", "png"]
    )

def _max_upload_mb() -> int:
    # Puedes sobreescribir en settings.MAX_UPLOAD_MB
    return int(getattr(settings, "MAX_UPLOAD_MB", 100))

def _bytes_limit() -> int:
    return _max_upload_mb() * 1024 * 1024

# -------- Ruta por proyecto: MEDIA_ROOT/archivos_tecnicos/p<ID>/<uuid>.<ext> --

def archivo_tecnico_upload_to(instance, filename):
    base, ext = os.path.splitext(filename)        # ("nombre", ".pdf")
    ext = (ext or ".bin").lower()
    return f"archivos_tecnicos/p{instance.project_id}/{uuid4().hex}{ext}"

# Alias de compatibilidad para migraciones antiguas (no borrar si existe 0004)
def archivos_project_path(instance, filename):
    return archivo_tecnico_upload_to(instance, filename)

# =============================== ArchivoTecnico ==============================

class ArchivoTecnico(models.Model):
    project = models.ForeignKey(
        'Project',
        on_delete=models.CASCADE,
        related_name='archivos',
    )

    archivo = models.FileField(
        upload_to=archivo_tecnico_upload_to,
        max_length=500,                     # evita errores 1406 en MySQL
        help_text="Archivo técnico a almacenar.",
    )

    # Metadatos
    nombre_original = models.CharField(max_length=255)
    tamano_bytes    = models.BigIntegerField(default=0)
    mime_type       = models.CharField(max_length=100, blank=True)
    descripcion     = models.TextField(blank=True)

    # Auditoría
    subido_por = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        null=True, blank=True,
        on_delete=models.SET_NULL,
    )
    subido_en = models.DateTimeField(default=timezone.now)

    class Meta:
        ordering = ["-subido_en"]
        indexes = [
            models.Index(fields=["project", "-subido_en"]),
            models.Index(fields=["mime_type"]),
            models.Index(fields=["subido_por"]),
        ]
        verbose_name = "Archivo técnico"
        verbose_name_plural = "Archivos técnicos"

    def __str__(self) -> str:
        base = self.nombre_original or os.path.basename(self.archivo.name)
        return f"{base} (Proyecto #{self.project_id})"

    # --------------------------- Validación del modelo -----------------------
    def clean(self):
        # Debe existir archivo
        if not self.archivo:
            raise ValidationError({"archivo": "Debes seleccionar un archivo."})

        # Tamaño
        size = 0
        try:
            size = int(getattr(self.archivo, "size", 0) or 0)
            if size == 0 and getattr(self.archivo, "name", None):
                size = int(self.archivo.storage.size(self.archivo.name))
        except Exception:
            size = 0

        if size <= 0:
            raise ValidationError({"archivo": "El archivo está vacío o es ilegible."})
        if size > _bytes_limit():
            raise ValidationError({"archivo": f"El archivo supera {_max_upload_mb()} MB."})

        # Extensión
        name_for_ext = getattr(self.archivo, "name", "") or self.nombre_original or ""
        ext = (os.path.splitext(name_for_ext)[1] or "").lower().lstrip(".")
        if ext not in _allowed_exts():
            allowed = ", ".join(f".{e}" for e in _allowed_exts())
            raise ValidationError({"archivo": f"Extensión no permitida: .{ext}. Permitidas: {allowed}."})

    # ----------------------- Guardado con metadatos --------------------------
    def save(self, *args, **kwargs):
        self.full_clean()  # activa clean() y validaciones de campos

        # nombre_original
        if not self.nombre_original and self.archivo:
            try:
                original = os.path.basename(getattr(self.archivo.file, "name", "") or "")
            except Exception:
                original = None
            if not original:
                original = os.path.basename(self.archivo.name)
            self.nombre_original = (original or "archivo")[:255]

        # tamano_bytes
        try:
            self.tamano_bytes = int(getattr(self.archivo, "size", 0) or 0)
            if self.tamano_bytes == 0 and getattr(self.archivo, "name", None):
                self.tamano_bytes = int(self.archivo.storage.size(self.archivo.name))
        except Exception:
            self.tamano_bytes = 0

        # mime_type
        if not self.mime_type:
            guess_from = self.nombre_original or self.archivo.name
            mime, _ = mimetypes.guess_type(guess_from)
            self.mime_type = mime or "application/octet-stream"

        super().save(*args, **kwargs)

    @property
    def tamano_legible(self) -> str:
        size = int(self.tamano_bytes or 0)
        for unit in ["bytes", "KB", "MB", "GB", "TB"]:
            if size < 1024 or unit == "TB":
                return f"{size:.0f} {unit}" if unit == "bytes" else f"{size:.1f} {unit}"
            size /= 1024.0