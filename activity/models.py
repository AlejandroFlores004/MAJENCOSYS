from django.db import models
from django.core.validators import MinLengthValidator, MinValueValidator, MaxValueValidator
from project.models import Project
from catalog.models import Material, ManoObra, Herramienta, Equipo, Riesgo, Calidad, Ambiental, Hidrologica
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
        validators=[MinValueValidator(Decimal("0.01")), MaxValueValidator(Decimal("0.99"))],
        null=False,
        blank=False,
        verbose_name="Prestaciones",
        help_text="Ingrese el porsentaje de prestaciones",
        default=0.1
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

class MemoryRiesgos(models.Model):
    activity = models.ForeignKey(
        Activity,
        on_delete=models.CASCADE,
        null=False,
        blank=False,
        related_name="memoryRiesgos_activity",
        verbose_name="Actividad",
        help_text="Actividad donde se evalúa el riesgo"
    )
    riesgo = models.ForeignKey(
        Riesgo,
        on_delete=models.SET_NULL,
        null=True,
        blank=False,
        related_name="memoryRiesgos_riesgo",
        verbose_name="Riesgo",
        help_text="Seleccione el riesgo correspondiente"
    )
    medida = models.CharField(
        max_length=150,
        null=False,
        blank=False,
        help_text="Ingrese la medida preventiva o correctiva aplicada",
        verbose_name="Medida_rsg",
        validators=[MinLengthValidator(3)]
    )
    descripcion_medida = models.TextField(
        max_length=300,
        null=True,
        blank=True,
        help_text="Describa brevemente la medida aplicada",
        verbose_name="Descripción_medida_rsg",
        validators=[MinLengthValidator(3)]
    )
    costo = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        validators=[MinValueValidator(Decimal("0.00"))],
        null=False,
        blank=False,
        default=0,
        verbose_name="Costo_rsg",
        help_text="Costo asociado a la medida de control o mitigación"
    )

    class Meta:
        verbose_name = "Memoria de riesgo"
        verbose_name_plural = "Memoria de riesgos"
        ordering = ["riesgo"]

    def __str__(self):
        return f"{self.activity.name} - {self.riesgo.name if self.riesgo else 'Sin riesgo definido'}"

    @property
    def project(self):
        return self.activity.project

    

class MemoryCalidad(models.Model):
    activity = models.ForeignKey(
        Activity,
        on_delete=models.CASCADE,
        null=False,
        blank=False,
        related_name="memoryCalidad_activity",
        verbose_name="Actividad",
        help_text="Actividad donde se aplica el control de calidad"
    )
    calidad = models.ForeignKey(
        Calidad,
        on_delete=models.SET_NULL,
        null=True,
        blank=False,
        related_name="memoryCalidad_calidad",
        verbose_name="Control de calidad",
        help_text="Seleccione el control de calidad correspondiente"
    )
    cantidad = models.PositiveIntegerField(
        null=False,
        blank=False,
        default=1,
        verbose_name="Cantidad_cld",
        help_text="Ingrese la cantidad de controles de calidad aplicados",
        validators=[MinValueValidator(1)]
    )
    responsable = models.CharField(
        max_length=150,
        null=False,
        blank=False,
        verbose_name="Responsable_cld",
        help_text="Ingrese el nombre del responsable del control de calidad",
        validators=[MinLengthValidator(3)]
    )

    class Meta:
        verbose_name = "Memoria de control de calidad"
        verbose_name_plural = "Memoria de controles de calidad"
        ordering = ["calidad"]

    def __str__(self):
        return f"{self.activity.name} - {self.calidad.name if self.calidad else 'Sin control de calidad definido'}"

    @property
    def project(self):
        return self.activity.project

class MemoryAmbiental(models.Model):
    activity = models.ForeignKey(
        Activity,
        on_delete=models.CASCADE,
        null=False,
        blank=False,
        related_name="memoryAmbiental_activity",
        verbose_name="Actividad",
        help_text="Actividad donde se aplica el control ambiental"
    )
    ambiental = models.ForeignKey(
        Ambiental,
        on_delete=models.SET_NULL,
        null=True,
        blank=False,
        related_name="memoryAmbiental_ambiental",
        verbose_name="Control ambiental",
        help_text="Seleccione el control ambiental correspondiente"
    )
    valor = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        validators=[MinValueValidator(Decimal("0.01"))],
        null=False,
        blank=False,
        default=0.00,
        verbose_name="Valor_mbt",
        help_text="Ingrese el valor asociado al control ambiental aplicado"
    )

    class Meta:
        verbose_name = "Memoria ambiental"
        verbose_name_plural = "Memorias ambientales"
        ordering = ["ambiental"]

    def __str__(self):
        return f"{self.activity.name} - {self.ambiental.name if self.ambiental else 'Sin control ambiental definido'}"

    @property
    def project(self):
        return self.activity.project


class MemoryHidrologica(models.Model):
    activity = models.ForeignKey(
        Activity,
        on_delete=models.CASCADE,
        null=False,
        blank=False,
        related_name="memoryHidrologica_activity",
        verbose_name="Actividad",
        help_text="Actividad donde se realiza la prueba hidrológica"
    )
    hidrologica = models.ForeignKey(
        Hidrologica,
        on_delete=models.SET_NULL,
        null=True,
        blank=False,
        related_name="memoryHidrologica_hidrologica",
        verbose_name="Prueba hidrológica",
        help_text="Seleccione la prueba hidrológica correspondiente"
    )
    costo = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        validators=[MinValueValidator(Decimal("0.01"))],
        null=False,
        blank=False,
        default=0.00,
        verbose_name="Costo_hdg",
        help_text="Ingrese el costo asociado a la prueba hidrológica"
    )

    class Meta:
        verbose_name = "Memoria hidrológica"
        verbose_name_plural = "Memorias hidrológicas"
        ordering = ["hidrologica"]

    def __str__(self):
        return f"{self.activity.name} - {self.hidrologica.name if self.hidrologica else 'Sin prueba definida'}"

    @property
    def project(self):
        return self.activity.project
