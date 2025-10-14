from django.db import models
from django.core.validators import MinLengthValidator, MinValueValidator
from project.models import Project
from catalog.models import Material, ManoObra, Herramienta, Equipo
from decimal import Decimal
# Create your models here.
class Activity(models.Model):
    name = models.CharField(
        max_length=200,
        null=False,
        blank=False,
        help_text="Ingrese el nombre de la actividad",
        verbose_name="Nombre",
        validators=[MinLengthValidator(3)]
    )
    project = models.ForeignKey(
        Project,
        on_delete=models.CASCADE,
        null=False,
        blank=False,
        related_name="activity_project"
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "Actividad"
        verbose_name_plural = "Actividades"
        ordering = ["name"]
        constraints = [
            models.UniqueConstraint(
                fields=["project", "name"],
                name="uniq_activity_name_per_project",
            )
        ]
    
    def __str__(self):
        return self.name

class Header(models.Model):
    activity = models.ForeignKey(
        Activity,
        on_delete=models.CASCADE,
        null=False,
        blank=False,
        related_name="header_activity",
        verbose_name="Actividad",
        help_text="Referencia a la actividad que pertenecen"
    )
    name = models.CharField(
        max_length=100,
        null=False,
        blank=False,
        help_text="Ingrese el nombre del encabezado",
        verbose_name="Nombre",
        validators=[MinLengthValidator(3)]
    )
    content = models.CharField(
        max_length=200,
        null=False,
        blank=False,
        help_text="Ingrese el contenido del encabezado",
        verbose_name="Contenido",
        validators=[MinLengthValidator(1)]
    )

    class Meta:
        verbose_name = "Encabezado"
        verbose_name_plural = "Encabezados"
        ordering = ["name"]
        constraints = [
            models.UniqueConstraint(
                fields=["activity", "name"],
                name="uniq_header_name_per_activity",
            )
        ]

    def __str__(self):
        return self.name
    

class MemoryMaterial(models.Model):
    activity = models.ForeignKey(
        Activity,
        on_delete=models.CASCADE,
        null=False,
        blank=False,
        related_name="memoryMaterial_activity",
        verbose_name="Actividad",
        help_text="Referencia a la actividad que pertenecen"
    )
    material = models.ForeignKey(
        Material,
        on_delete=models.SET_NULL,
        null=True,
        blank=False,
        related_name="memoryMaterial_material",
        verbose_name="Material",
        help_text="Seleccione el material a usar"
    )
    quantity = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        validators=[MinValueValidator(Decimal("0.01"))],
        null=False,
        blank=False,
        verbose_name="Cantidad",
        help_text="Ingrese la cantidad de materiales a usar",
        default=1
    )
    class Meta:
        verbose_name = "Memoria de material"
        verbose_name_plural = "Memoria de materiales"
        ordering = ["material"]

    def __str__(self):
        return self.activity.name

class MemoryManoObra(models.Model):
    activity = models.ForeignKey(
        Activity,
        on_delete=models.CASCADE,
        null=False,
        blank=False,
        related_name="MemoryManoObra_activity",
        verbose_name="Actividad",
        help_text="Referencia a la actividad que pertenecen"
    )
    manoobra = models.ForeignKey(
        ManoObra,
        on_delete=models.SET_NULL,
        null=True,
        blank=False,
        related_name="memoryManoObra_manoobra",
        verbose_name="ManoObra",
        help_text="Seleccione la mano de obra a usar"
    )
    prestaciones = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        validators=[MinValueValidator(Decimal("0.01"))],
        null=False,
        blank=False,
        verbose_name="Prestaciones",
        help_text="Ingrese el porsentaje de prestaciones",
        default=1
    )
    rendimiento = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        validators=[MinValueValidator(Decimal("0.01"))],
        null=False,
        blank=False,
        verbose_name="Rendimiento",
        help_text="Ingrese la cantidad de rendimiento",
        default=1
    )
    class Meta:
        verbose_name = "Memoria de mano de obra"
        verbose_name_plural = "Memoria de manos de obra"
        ordering = ["manoobra"]

    def __str__(self):
        return self.activity.name

class MemoryHerramienta(models.Model):
    activity = models.ForeignKey(
        Activity,
        on_delete=models.CASCADE,
        null=False,
        blank=False,
        related_name="MemoryHerramienta_activity",
        verbose_name="Actividad",
        help_text="Referencia a la actividad que pertenecen"
    )
    herramienta = models.ForeignKey(
        Herramienta,
        on_delete=models.SET_NULL,
        null=True,
        blank=False,
        related_name="memoryHerramienta_herramienta",
        verbose_name="Herramienta",
        help_text="Seleccione la herramienta a usar"
    )
    rendimiento = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        validators=[MinValueValidator(Decimal("0.01"))],
        null=False,
        blank=False,
        verbose_name="Rendimiento_hrr",
        help_text="Ingrese la cantidad de rendimiento",
        default=1
    )
    class Meta:
        verbose_name = "Memoria de herramienta"
        verbose_name_plural = "Memoria de herramientas"
        ordering = ["herramienta"]

    def __str__(self):
        return self.activity.name

class MemoryEquipo(models.Model):
    activity = models.ForeignKey(
        Activity,
        on_delete=models.CASCADE,
        null=False,
        blank=False,
        related_name="MemoryEquipo_activity",
        verbose_name="Actividad",
        help_text="Referencia a la actividad que pertenecen"
    )
    equipo = models.ForeignKey(
        Equipo,
        on_delete=models.SET_NULL,
        null=True,
        blank=False,
        related_name="memoryEquipo_equipo",
        verbose_name="Equipo",
        help_text="Seleccione la equipo a usar"
    )
    rendimiento = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        validators=[MinValueValidator(Decimal("0.01"))],
        null=False,
        blank=False,
        verbose_name="Rendimiento_eqp",
        help_text="Ingrese la cantidad de rendimiento",
        default=1
    )
    class Meta:
        verbose_name = "Memoria de equipo"
        verbose_name_plural = "Memoria de equipos"
        ordering = ["equipo"]

    def __str__(self):
        return self.activity.name
