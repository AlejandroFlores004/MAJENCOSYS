from django.db import models
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from django.core.files.storage import default_storage

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
