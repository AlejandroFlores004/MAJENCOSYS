from django.db import models
from django.contrib.auth.models import User
from django.db import models
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
import os

# Opciones de estado del proyecto
opcionesEstadoProyecto = [
    ('PL', 'Planeación'),
    ('P', 'En Proceso'),
    ('C', 'Completado'),
]

opcionesTypeProyecto = [
    ('INF', 'Infraestructura'),
    ('OBM', 'Obras de Mitigación'),
    ('ALC', 'Alcantarillado'),
    ('CMRV', 'Construcción y Mantenimiento de Red Vial'),
]

def validate_image_size(image):
    limit = 5 * 1024 * 1024  # 5MB
    if image.size > limit:
        raise ValidationError('El tamaño de la imagen no puede superar los 5MB.')

def validate_image_extension(image):
    ext = os.path.splitext(image.name)[1]
    if ext.lower() not in ['.jpg', '.jpeg', '.png']:
        raise ValidationError('La imagen debe ser en formato .jpg, .jpeg o .png.')

class Project(models.Model):
    # Nombre del proyecto
    nombre = models.CharField(
        "Nombre",
        max_length=255,
        blank=False,
        null=False,
        help_text="Nombre del Proyecto a crear"
    )

    #Cliente
    cliente = models.CharField(
        "Cliente",
       max_length=255,
        blank= False,
        null=False,
        help_text="Cliente del Proyecto"
    )

    # Descripción del proyecto
    descripcion = models.TextField(
        "Descripción",
        blank=False,
        null=False,
        help_text="Descripción del Proyecto"
    )

    # Estado del proyecto
    estado = models.CharField(
        "Estado",
        max_length=2,
        choices=opcionesEstadoProyecto,
        default='PL',
    )

    # Usuario que creó el proyecto
    usuario = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='usuarioProyecto'
    )

    # Usuario técnico asignado
    tecnico = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='tecnicoProyecto'
    )

    # Fecha de creación del proyecto
    created_at = models.DateTimeField(auto_now_add=True)

    # Última modificación (último acceso)
    updated_at = models.DateTimeField(auto_now=True)

    # Tipos de Proyecto
    type = models.CharField(
        "Tipo",
        max_length=4,
        choices=opcionesTypeProyecto,
        default='INF',
    )

    # Imagen de Proyecto
    imagen = models.ImageField(
        "Imagen Proyecto",
        upload_to='imgProjects/',
        null=True,
        blank=True,
        validators=[validate_image_size, validate_image_extension]
    )

    # Representación en texto del proyecto
    def __str__(self):
        return f"Proyecto {self.nombre} - {self.descripcion[:35]}..."
