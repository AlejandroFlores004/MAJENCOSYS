from django.db import models
from django.core.validators import MinValueValidator
from project.models import Project
from decimal import Decimal
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError

class Unit(models.Model):
    name = models.CharField("Nombre", max_length=100, unique=True, null=False, blank= False)
    abbreviation = models.CharField("Abreviatura", max_length=10, unique=True, null=False, blank= False, help_text="Usa una abreviatura corta, p. ej., kg, m, u.") 

    class Meta:
        verbose_name = "Unidad"
        verbose_name_plural = "Unidades"
        ordering = ["name"]

    def __str__(self):  
        return f"{self.name} ({self.abbreviation})"


class Material(models.Model):
    name = models.CharField("Nombre", max_length=100, null=False, blank= False)
    description = models.TextField("Descripción del material", null=True, blank= True)
    price = models.DecimalField(
        "Precio",
        max_digits=10,
        decimal_places=2,
        validators=[MinValueValidator(Decimal("0.01"))],
        null=False, blank= False
    )
    unit = models.ForeignKey(
        Unit,
        on_delete=models.SET_NULL,   
        null=True,                   
        blank=True,                  
        related_name="materials"
    )
    project = models.ForeignKey(
        Project,
        on_delete=models.CASCADE,
        null=False,
        blank=False,
        related_name="proyecto_materiales"
    )

    class Meta:
        verbose_name = "Material"
        verbose_name_plural = "Materiales"
        ordering = ["name"]
        indexes = [models.Index(fields=["name"])]

    def __str__(self):
        u = self.unit.abbreviation if self.unit else "sin unidad"
        return f"{self.name} - {u} - ${self.price}"


class Labour(models.Model):
    name = models.CharField("Nombre", max_length=100, null=False, blank= False)
    description = models.TextField("Descripción de la mano de obra", null=True, blank= True)
    price = models.DecimalField(
        "Valor de la jornada",
        max_digits=10,
        decimal_places=2,
        validators=[MinValueValidator(Decimal("0.01"))]
    )
    project = models.ForeignKey(
        Project,
        on_delete=models.CASCADE,
        null=False,
        blank=False,
        related_name="proyecto_mano_de_obra"
    )

    class Meta:
        verbose_name = "Mano de obra"
        verbose_name_plural = "Listado mano de obra"
        ordering = ["name"]

    def __str__(self):
        return f"{self.name} - ${self.price}"
    
class Tool(models.Model):
    name = models.CharField("Nombre", max_length=100, null=False, blank= False)
    dayCost = models.DecimalField(
        "Valor por día",
        max_digits=10,
        decimal_places=2,
        validators=[MinValueValidator(Decimal("0.01"))]
    )
    project = models.ForeignKey(
        Project,
        on_delete=models.CASCADE,
        null=False,
        blank=False,
        related_name="proyecto_herramienta"
    )
    
    def __str__(self):
        return f"{self.name} - ${self.dayCost}"
    
    class Meta:
        verbose_name = "Herramienta o equipo"
        verbose_name_plural = "Herramientas y equipos"
        ordering = ["name"]
        indexes = [models.Index(fields=["name"])]


class HeavyMachinery(models.Model):
    FUNCION_CHOICES = [
        ('MOV_TIERRA', 'Movimiento de tierra'),
        ('TRANSPORTE', 'Transporte y acarreo'),
        ('ELEVACION', 'Elevación y carga'),
        ('COMPACTACION', 'Compactación'),
        ('PAVIMENTACION', 'Pavimentación'),
        ('PERFORACION', 'Perforación y demolición'),
        ('APOYO', 'Maquinaria especial o de apoyo'),
    ]
    name = models.CharField("Nombre", max_length=100, null=False, blank= False)
    function = models.CharField(
        max_length=20,
        choices=FUNCION_CHOICES,
        verbose_name="Función de la maquinaria"
    )
    capacity = models.CharField(max_length=50, blank=True, null=True)
    price = models.DecimalField(
        "Precio",
        max_digits=10,
        decimal_places=2,
        validators=[MinValueValidator(Decimal("0.01"))],
        null=False, blank= False
    )

    project = models.ForeignKey(
        Project,
        on_delete=models.CASCADE,
        null=False,
        blank=False,
        related_name="proyecto_maquinaria_pesada"
    )

    class Meta:
        verbose_name = "Maquinaria pesada"
        verbose_name_plural = "Maquinarias pesadas"
        ordering = ['name']
        
    def __str__(self):
        return f"{self.name} ({self.get_function_display()})"

class QualityControl(models.Model):
    name = models.CharField("Nombre de la prueba", max_length=100, null=False, blank=False)
    description = models.TextField("Descripción", blank=True, null=True)

    responsible = models.ForeignKey(
        User,
        on_delete=models.PROTECT,
        limit_choices_to={'groups__name': 'Supervisor'},
        verbose_name="Responsable (Supervisor)"
    )
    project = models.ForeignKey(
        Project,
        on_delete=models.CASCADE,
        null=False,
        blank=False,
        related_name="proyecto_control_calidad"
    )
    def clean(self):
        """Validación adicional para asegurar que el usuario pertenece al grupo Supervisor."""
        if not self.responsible.groups.filter(name='Supervisor').exists():
            raise ValidationError("El responsable debe pertenecer al grupo 'Supervisor'.")
        

    class Meta:
        verbose_name = "Prueba de control de calidad"
        verbose_name_plural = "Pruebas de control de calidad"
        ordering = ['name']

    def __str__(self):
        return f"{self.name} - {self.responsible.get_full_name() or self.responsible.username}"